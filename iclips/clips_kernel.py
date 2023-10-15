# This file is part of iCLIPS.

# ICLIPS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# ICLIPS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with ICLIPS. If not, see <http://www.gnu.org/licenses/>.


import glob
import contextlib
from io import StringIO
from enum import IntEnum
from traceback import format_exc
from difflib import get_close_matches

import clips
import regex
from ipykernel.kernelbase import Kernel

from iclips import __version__
from iclips.common import KEYWORDS, BUILTINS


class CLIPSKernel(Kernel):
    banner = 'iCLIPS'
    implementation = 'CLIPS'
    implementation_version = __version__
    language_info = {'name': 'clips',
                     'version': '6.41',
                     'file_extension': '.clp',
                     'mimetype': 'text/x-clips',
                     'codemirror_mode': 'clips'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cell_mode = CellMode.CLIPS
        # I/O Routers
        self.clips_input = InputRouter(self)
        self.clips_output = OutputRouter()
        # CLIPS Environment
        self.environment = clips.Environment()
        self.environment.add_router(self.clips_input)
        self.environment.add_router(self.clips_output)
        global_environment(self.environment)

    def do_execute(
            self,
            code: str,
            silent: bool,
            _store_history: bool=True,
            _user_expressions: dict=None,
            allow_stdin: bool=False,
            *_
    ) -> dict:
        """Code execution request handler."""
        self._allow_stdin = allow_stdin

        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count}

        if code.startswith("%%"):
            status = self.magic_cell(code, silent)
        elif self.cell_mode == CellMode.CLIPS:
            status = self.clips_code_cell(code, silent)
        elif self.cell_mode in (CellMode.PYTHON, CellMode.DEFPYFUNCTION):
            status = self.python_code_cell(code, silent)
            self.cell_mode = CellMode.CLIPS

        return status

    def do_complete(self, code: str, cursor: int) -> int:
        """Code completion request handler."""
        token = code[:cursor].split()[-1].strip('()"')
        completion = self.completion_list(code, token)

        matches = [m for m in
                   get_close_matches(token, completion, n=100, cutoff=0.1)
                   if m.startswith(token)]

        return {'status': 'ok',
                'cursor_start': cursor - len(token),
                'cursor_end': cursor,
                'matches': matches}

    def do_is_complete(self, code: str) -> dict:
        """Newline continuation checker."""
        if self.cell_mode == CellMode.CLIPS:
            indent = '  '
            status = 'complete' if even_parenthesis(code) else 'incomplete'
        elif self.cell_mode in (CellMode.PYTHON, CellMode.DEFPYFUNCTION):
            indent = ''
            status = 'complete' if code.endswith('\n\n') else 'incomplete'

        return {'status': status, 'indent': indent}

    def magic_cell(self, code: str, silent: bool, *_) -> dict:
        """Handle a cell containing Magic commands."""
        status = 'ok'
        magic = code.lstrip('%').strip()

        if magic == 'python':
            self.cell_mode = CellMode.PYTHON
            text = "Python mode: return twice to execute the inserted code.\n"
        elif magic == 'define-python-function':
            self.cell_mode = CellMode.DEFPYFUNCTION
            text = "DefPyFunction mode: return twice " + \
                   "to define the inserted function within CLIPS.\n"
        else:
            status = 'error'
            text = "Unrecognised magic command\n"

        if not silent:
            stream = {'name': 'stdout', 'text': text}

            self.send_response(self.iopub_socket, 'stream', stream)

        return {'status': status, 'execution_count': self.execution_count}

    def clips_code_cell(self, code: str, silent: bool, *_) -> dict:
        """Handle a code cell containing CLIPS code."""
        output = ''
        status = 'ok'
        uncommented_code = regex.sub(r';.*', '', code)
        commands = regex.findall(PARENTHESES_REGEX, uncommented_code)

        for command in commands:
            try:
                result = self.execute_clips_code(command.strip())
                output += self.clips_output.output + '\n' + str(result)
            except RuntimeError:
                status = 'error'
                output += self.clips_output.output

        if not silent:
            stream = {'name': 'stdout', 'text': output.strip()}

            self.send_response(self.iopub_socket, 'stream', stream)

        return {'status': status, 'execution_count': self.execution_count}

    def python_code_cell(self, code: str, silent: bool, *_) -> dict:
        """Handle a code cell containing Python code."""
        output = ''
        status = 'ok'

        with capture_python_output() as python_output:
            try:
                exec(code, globals())

                if self.cell_mode == CellMode.DEFPYFUNCTION:
                    self.define_python_function(code)
            except Exception:
                status = 'error'
                output = format_exc()

        output = python_output.getvalue() + '\n' + output

        if not silent:
            stream = {'name': 'stdout', 'text': output}

            self.send_response(self.iopub_socket, 'stream', stream)

        return {'status': status, 'execution_count': self.execution_count}

    def define_python_function(self, code: str) -> tuple:
        match = regex.search(FUNCNAME_REGEX, code)

        try:
            funcname = match.group(1)
            function = globals()[funcname]

            self.environment.define_function(function)
        except (LookupError, AttributeError):
            raise RuntimeError("No function definition found")
        except clips.CLIPSError as error:
            self.clips_output.reset()
            raise RuntimeError("Unable to define function in CLIPS") from error

    def execute_clips_code(self, code: str) -> str:
        """Evaluate CLIPS code."""
        result = None
        function = code.strip('()').split()[0]

        try:
            if function in DEFCONSTRUCTS:
                self.environment.build(code)
            else:
                result = self.environment.eval(code)
        except clips.CLIPSError as error:
            raise RuntimeError(error)

        return str(result) if result is not None else ''

    def completion_list(self, code: str, token: str) -> list:
        """Return a list of completion candidates."""
        completion = list(COMPLETION)
        completion += [t for t in code.strip('()').split() if t != token]

        classes = list(self.environment.classes())
        completion.extend((c.name for c in classes))
        completion.extend((s.name for c in classes for s in c.slots()))

        templates = list(self.environment.templates())
        completion.extend((t.name for t in templates))
        completion.extend((s.name for t in templates for s in t.slots))

        completion.extend((g.name for g in self.environment.generics()))
        completion.extend((f.name for f in self.environment.functions()))
        completion.extend((g.name for g in self.environment.globals()))
        completion.extend(glob.glob(token + '*'))

        return completion


class InputRouter(clips.Router):
    """CLIPS Router for capturing input requests."""
    def __init__(self, kernel):
        super().__init__('iclips-input-router', 40)
        self._input = None
        self._kernel = kernel

    def query(self, name: str) -> bool:
        return name == 'stdin'

    def read(self, _name: str) -> int:
        """Returns the next character in the input.
        If the input buffer is empty, it requests from the client.

        """
        if self._input is None:
            # raw_input truncates the newline
            self._input = iter(self._kernel.raw_input())

        try:
            return ord(next(self._input))
        except StopIteration:
            self._input = None

            return ord('\n')


class OutputRouter(clips.Router):
    """CLIPS Router for capturing output requests."""
    ROUTERS = {'stdout', 'stderr', 'stdwrn'}

    def __init__(self):
        super().__init__('iclips-output-router', 40)
        self._output = ''

    @property
    def output(self) -> str:
        ret = self._output
        self._output = ''

        return ret

    def query(self, name: str) -> bool:
        return name in self.ROUTERS

    def write(self, _name: str, message: str):
        """Appends the CLIPS message to the output."""
        self._output += message


def even_parenthesis(code: str) -> bool:
    counter = 0
    string = False

    for character in code:
        if character == '"':
            string = False if string else True
        elif not string and character == '(':
            counter += 1
        elif not string and character == ')':
            counter -= 1

        if counter < 0:
            return False

    return counter == 0


def global_environment(environment):
    global CLIPS
    CLIPS = environment


@contextlib.contextmanager
def capture_python_output() -> StringIO:
    """Yield a buffer capturing stdout and stderr.

    The buffer content is available only outside of the context manager.

    """
    output = StringIO()
    stdout = StringIO()
    stderr = StringIO()

    with contextlib.redirect_stdout(stdout):
        with contextlib.redirect_stderr(stderr):
            try:
                yield output
            finally:
                output.write(stdout.getvalue() + stderr.getvalue())


class CellMode(IntEnum):
    CLIPS = 0
    PYTHON = 1
    DEFPYFUNCTION = 2


CLIPS = None
FUNCNAME_REGEX = r'def (.*)\(.*\)'
PARENTHESES_REGEX = r'([^()]*\((?:[^()]++|(?R))*+\))'
MAGIC_COMMANDS = 'python', 'define-python-function'
COMPLETION = KEYWORDS + BUILTINS + MAGIC_COMMANDS
DEFCONSTRUCTS = ('deftemplate', 'deffunction', 'defmodule',
                 'defrule', 'defclass', 'defglobal', 'deffacts')


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=CLIPSKernel)
