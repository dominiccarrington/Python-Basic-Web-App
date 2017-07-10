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
from .Script import Script
from ..Lexer import Lexer, VARIABLE_MATCH

class Echo(Script):
    def __init__(self):
        super(Echo, self).__init__("", p=True)
        self.addSyntax("$$")
        self.addArgument("var", allowed=VARIABLE_MATCH)

    def run(self):
        return str(Lexer.getArg(self.arguments["var"]))

class Run(Script):
    def __init__(self):
        super(Run, self).__init__("run")
        self.addArgument("class", allowed=r"\w_")
        self.addSyntax(".")
        self.addArgument("method", allowed=r"\w_")
        self.addSyntax("(")
        self.addArgument("params", allowed=r"^\)")
        self.addSyntax(")")

class Include(Script):
    def __init__(self):
        super(Include, self).__init__("include")
        self.addArgument("file", allowed=r"^\)")

class Route(Script):
    def __init__(self, router):
        super(Route, self).__init__("route")
        self.router = router
        self.addArgument("route", allowed=VARIABLE_MATCH)
        self.addNonCapGroup(lambda group: group.addSyntax("(").addArgument("options", allowed=r"^\)", optional=True, default="").addSyntax(")"))

    def run(self):
        named_route = self.arguments["route"]
        ps = {}
        options = self.arguments["options"]
        if options:
            params = options.split(";")

            for param in params:
                sections = param.strip().split("=")
                if len(sections) == 2:
                    ps[sections[0].strip()] = sections[1].strip()

        url = self.router.get_path_from_name(named_route, **ps)
        return url

class Set(Script):
    def __init__(self):
        super(Set, self).__init__("set")
        self.addSyntax("$$")
        self.addArgument("var", allowed=VARIABLE_MATCH)
        self.addSyntax("=")
        self.addSyntax("\"")
        self.addArgument("value", allowed=r"^\"")
        self.addSyntax("\"")

    def run(self):
        Lexer.setArg(self.arguments["var"], self.arguments["value"])
