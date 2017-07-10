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
VARIABLE_MATCH = r"\w\d\._-"

class Lexer:
    _scripts = []
    args = {}

    @staticmethod
    def registerScript(script):
        Lexer._scripts.append(script)

    @staticmethod
    def convertCode(code, args=None):
        if args is not None:
            Lexer.args = DotDict(args)

        for script in Lexer._scripts:
            try:
                code = script.check(code)
            except (ValueError, TypeError) as e:
                print(str(e))

        return code

    @staticmethod
    def getArg(path):
        path = str(path).split(".")
        args = Lexer.args
        for bit in path:
            if bit in args:
                args = args[bit]

        return args

    @staticmethod
    def setArg(find, value):
        Lexer.args.__setitem__(find, value)

class DotDict(dict):
    """
    @link https://stackoverflow.com/questions/3797957/python-easily-access-deeply-nested-dict-get-and-set
    """
    def __init__(self, value=None):
        if value is None:
            pass
        elif isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        else:
            raise TypeError('Expected dict')

    def __setitem__(self, key, value):
        if '.' in key:
            myKey, restOfKey = key.split('.', 1)
            target = self.setdefault(myKey, DotDict())
            if not isinstance(target, DotDict):
                raise KeyError('cannot set "{}" in "{}" ({})' % (restOfKey, myKey, repr(target)))
            target[restOfKey] = value
        else:
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if '.' not in key:
            return dict.__getitem__(self, key)
        myKey, restOfKey = key.split('.', 1)
        target = dict.__getitem__(self, myKey)
        if not isinstance(target, DotDict):
            raise KeyError('cannot get "{}" in "{}" ({})' % (restOfKey, myKey, repr(target)))
        return target[restOfKey]

    def __contains__(self, key):
        if '.' not in key:
            return dict.__contains__(self, key)
        myKey, restOfKey = key.split('.', 1)
        target = dict.__getitem__(self, myKey)
        if not isinstance(target, DotDict):
            return False
        return restOfKey in target

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]

    __setattr__ = __setitem__
    __getattr__ = __getitem__
