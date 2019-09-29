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

# -*- coding: utf-8 -*-

"""Lexers for CLIPS language."""

import re

from pygments.lexer import RegexLexer
from pygments.token import Number, Punctuation, String
from pygments.token import Text, Comment, Operator, Keyword, Name

from iclips.common import KEYWORDS, BUILTINS


__all__ = ['CLIPSLexer']


class CLIPSLexer(RegexLexer):
    """A CLIPS lexer, parsing a stream and outputting the tokens
    needed to highlight CLIPS code.

    """
    name = 'CLIPS'
    aliases = ['clips', 'clp']
    filenames = ['*.clp']
    mimetypes = ['text/x-clips', 'application/x-clips']
    keywords = KEYWORDS
    builtins = BUILTINS
    valid_name = r'[\w!$%*+,/:<=>@^~|-]+'
    tokens = {'root': ((r';.*$', Comment.Single),
                       (r'\s+', Text),
                       (r'-?\d+\.\d+', Number.Float),
                       (r'-?\d+', Number.Integer),
                       (r'"(\\\\|\\"|[^"])*"', String),
                       (r'(TRUE|FALSE|nil)', Name.Constant),
                       (r"('|#|`|,@|,|\.)", Operator),
                       (r'(%s)' % '|'.join(re.escape(entry)
                                           for entry in keywords),
                        Keyword),
                       (r"(?<=\()(%s)" % '|'.join(re.escape(entry)
                                                  for entry in builtins),
                        Name.Builtin),
                       (r'\?' + valid_name, Name.Label),
                       (r'(\(|\))', Punctuation),
                       (r'(\[|\])', Punctuation),
                       (valid_name, Text))}
