from difflib import get_close_matches

import clips

from ipykernel.kernelbase import Kernel

from iclips.common import KEYWORDS, BUILTINS


class CLIPSKernel(Kernel):
    banner = 'ICLIPS'
    implementation = 'CLIPS'
    implementation_version = '0.0.1'
    language_info = {'name': 'clips',
                     'version': '6.30',
                     'file_extension': 'clp',
                     'mimetype': 'text/x-clips'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environment = clips.Environment()

    def do_execute(self, code: str, silent: bool, *_) -> dict:
        """Code execution request handler."""
        status = 'ok'

        try:
            result = self.eval_code(code) if code else ''

            if not silent:
                stream_content = {'name': 'stdout', 'text': result}
                self.send_response(self.iopub_socket, 'stream', stream_content)
        except RuntimeError:
            status = 'error'

        return {'status': status, 'execution_count': self.execution_count}

    def do_complete(self, code: str, cursor: int) -> int:
        """Code completion request handler."""
        token = code[:cursor].split()[-1].strip('()')

        matches = [m for m in
                   get_close_matches(token, COMPLETION, n=25, cutoff=0.1)
                   if m.startswith(token)]

        return {'status': 'ok',
                'cursor_start': cursor - len(token),
                'cursor_end': cursor,
                'matches': matches}

    def do_is_complete(self, code: str) -> dict:
        """Newline continuation checker."""
        status = 'complete' if even_parenthesis(code) else 'incomplete'

        return {'status': status, 'indent': '  '}

    def eval_code(self, code: str) -> str:
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
