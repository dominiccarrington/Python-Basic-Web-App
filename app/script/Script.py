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
import re
import math
from ..Lexer import VARIABLE_MATCH, VARIABLE, Lexer

class Script:
    def __init__(self, name, p=False):
        self.name = name
        self.p = p
        self.pattern = r"{" + ("%" if p else "{") + r"\s*(?:" + name + r"\s*"
        self.arguments = ArgumentList()
        self.finished = False

    def addArgument(self, name, allowed=".", optional=False, default=None, minLength=1, maxLength=math.inf, variableAllowed=False, shouldVarExist=True):
        if optional and default is None:
            raise ValueError("Optional Argument must have a default value")
        # self.arguments[name] = (None if not optional else default)
        self.arguments[name] = Argument(name, optional, default, variableAllowed, shouldVarExist)

        length = "*"
        if minLength <= 0 or maxLength == math.inf:
            length = "*"
        elif minLength == 1 and maxLength == math.inf:
            length = "+"
        elif minLength >= 0 and maxLength < math.inf:
            length = "{" + str(minLength) + "," + str(maxLength) + "}"

        self.pattern += "(?P<" + name + ">"
        if allowed:
            self.pattern += ("." if allowed == "." else "[" + allowed + "]") + length
        if allowed and variableAllowed:
            self.pattern += "|"
        if variableAllowed:
            self.pattern += r"\$\$[" + VARIABLE_MATCH + r"]+"
        self.pattern += ")" + ("?" if optional else "") + r"\s*"
        return self

    def addSyntax(self, chars, required=True):
        self.pattern += re.escape(chars) + ("?" if not required else "") + r"\s*"
        return self

    def addNonCapGroup(self, contents, optional=True):
        self.pattern += "(?:"
        contents(self)
        self.pattern += ")" + ("?" if optional else "") + r"\s*"

    def run(self):
        raise NotImplementedError

    def check(self, body):
        if not self.finished:
            self.finish()
            self.finished = True
            self.pattern = re.compile(self.pattern)

        orgi = self.arguments
        for m in self.pattern.finditer(body):
            print(self.arguments)
            for k in self.arguments.keys():
                group = m.group(k)
                # self.arguments[k] = (group if group != "" else self.arguments[k])
                self.arguments[k].setValue(group)
            #print(m.group(0))
            r = self.run()
            body = body.replace(m.group(0), r if r is not None else "")
            self.arguments = orgi
        return body

    def finish(self):
        self.pattern += r")\s*" + ("%" if self.p else "}") + r"}"
        #print(self.pattern)
        self.finished = True

class Block(Script):
    def __init__(self, name):
        super(Block, self).__init__(name)
        self.arguments["content"] = Argument("content")

    def addArgument(self, name, allowed=".", optional=False, default=None, minLength=1, maxLength=math.inf, variableAllowed=False, shouldVarExist=True):
        if name == "content":
            raise ValueError
        return super().addArgument(name=name, allowed=allowed, optional=optional, default=default, minLength=minLength, maxLength=maxLength, variableAllowed=variableAllowed)

    def finish(self):
        self.pattern += r")\s*}}(?P<content>(?:.|\n)*){{\s*end" + self.name + r"\s*}}"

    def run(self):
        raise NotImplementedError

class Argument:
    def __init__(self, name, optional=False, default=None, variableAllowed=False, shouldVarExist=True):
        self.name = name
        self.value = None
        self.optional = optional
        self.default = default
        self.variableAllowed = variableAllowed
        self.shouldVarExist = shouldVarExist

    def setValue(self, val=None):
        if val:
            if self.variableAllowed:
                m = VARIABLE.match(val)
                if m:
                    var = m.group(1)
                    if self.shouldVarExist:
                        self.value = Lexer.getArg(var)
                    else:
                        self.value = var
            else:
                self.value = val
        elif self.optional:
            self.value = self.default

    def getValue(self):
        return self.value

    def __str__(self):
        return self.getValue()

class ArgumentList(dict):
    def __init__(self, **elements):
        super(ArgumentList, self).__init__(**elements)

    def __getitem__(self, item):
        item = super(ArgumentList, self).__getitem__(item)
        if isinstance(item, Argument):
            return item.getValue()
        return TypeError