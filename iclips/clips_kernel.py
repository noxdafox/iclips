from difflib import get_close_matches

from ipykernel.kernelbase import Kernel
from clips import CLIPSError, Environment, Router

from iclips.common import KEYWORDS, BUILTINS


class CLIPSKernel(Kernel):
    banner = 'iCLIPS'
    implementation = 'CLIPS'
    implementation_version = '0.0.1'
    language_info = {'name': 'clips',
                     'version': '6.30',
                     'file_extension': 'clp',
                     'mimetype': 'text/x-clips'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environment = Environment()
        self.output = OutputRouter()
        self.output.add_to_environment(self.environment)

    def do_execute(self, code: str, silent: bool, *_) -> dict:
        """Code execution request handler."""
        output = ''
        status = 'ok'

        if not code.strip():
            return {'status': status, 'execution_count': self.execution_count}

        try:
            result = self.execute_code(code)
            output = self.output.output + '\n' + str(result)
        except RuntimeError:
            status = 'error'
            output = self.output.output
        finally:
            if not silent:
                stream = {'name': 'stdout', 'text': output.strip()}

                self.send_response(self.iopub_socket, 'stream', stream)

        return {'status': status, 'execution_count': self.execution_count}

    def do_complete(self, code: str, cursor: int) -> int:
        """Code completion request handler."""
        token = code[:cursor].split()[-1].strip('()')
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
        status = 'complete' if even_parenthesis(code) else 'incomplete'

        return {'status': status, 'indent': '  '}

    def execute_code(self, code: str) -> str:
        """Evaluate CLIPS code."""
        result = None
        function = code.strip('()').split()[0]

        try:
            if function in DEFCONSTRUCTS:
                self.environment.build(code)
            else:
                result = self.environment.eval(code)
        except CLIPSError as error:
            raise RuntimeError(error)

        return str(result) if result is not None else ''

    def completion_list(self, code, token):
        completion = list(COMPLETION)
        completion += [t for t in code.strip('()').split() if t != token]

        classes = [c for c in self.environment.classes()]
        completion.extend((c.name for c in classes))
        completion.extend((s.name for c in classes for s in c.slots()))
        templates = [t for t in self.environment.templates()]
        completion.extend((t.name for t in templates))
        completion.extend((s.name for t in templates for s in t.slots()))

        return completion


class OutputRouter(Router):
    """CLIPS Router for capturing stdout."""
    ROUTERS = {'wtrace', 'stdout', 'wclips', 'wdialog',
               'wdisplay', 'wwarning', 'werror'}

    def __init__(self):
        super().__init__('iclips-output-router', 30)
        self._output = ''

    @property
    def output(self) -> str:
        ret = self._output

        self._output = ''

        return ret

    def query(self, name: str) -> bool:
        return name in self.ROUTERS

    def print(self, _, message: str):
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


COMPLETION = KEYWORDS + BUILTINS
DEFCONSTRUCTS = ('deftemplate', 'deffunction', 'defmodule',
                 'defrule', 'defclass', 'defglobal')


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=CLIPSKernel)
