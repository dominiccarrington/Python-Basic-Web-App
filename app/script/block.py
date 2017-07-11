"""
Basic Python Web Application
Copyright (C) 2017 Dominic Carrington

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from .Script import Block
from ..Lexer import Lexer

class For(Block):
    def __init__(self):
        super(For, self).__init__("for")
        self.addArgument("var", allowed=None, variableAllowed=True, shouldVarExist=False)
        self.addArgument("start", allowed=r"-\d", variableAllowed=True)
        self.addArgument("stop", allowed=r"-\d", variableAllowed=True)
        self.addArgument("step", allowed=r"-\d", optional=True, default=1, variableAllowed=True)

    def run(self):
        var = str(self.arguments['var'])
        start = int(self.arguments['start'])
        stop = int(self.arguments['stop'])
        step = int(self.arguments['step'])
        content = str(self.arguments['content'])

        if step == 0:
            return "Error: Step must be not be 0"
        elif step < 0 and stop > start:
            return "Error: Start must be smaller than stop if the step if less than 0"
        elif step > 0 and start > stop:
            return "Error: Stop must be greater than start if the step if greater than 0"

        repl = ""
        for _loop in range(start, stop, step):
            Lexer.args[var] = _loop
            repl += Lexer.convertCode(content)
        del Lexer.args[var]

        return repl
