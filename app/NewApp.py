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
from .diy_framework import App, Router
from .diy_framework.http_utils import Response
from .diy_framework.application import logger
from .helper.Timer import Timer
from .Lexer import Lexer
from .script.block import For
from .script.inline import Echo, Set, Route

app = None
router = None

def createResponse(r, html, **args):
    Timer.start("Response")
    if "app" not in args.keys():
        args["app"] = {}
        args["app"]["host"] = str(app.host)
        args["app"]["port"] = str(app.port)
        args["app"]["base_url"] = "http://" + str(app.host)+ ":" + str(app.port)
    if "request" not in args.keys():
        args["request"] = {}
        args["request"]["method"] = r.method

        query = {}
        for k, v in r.query_params.items():
            query[k] = v[0]
        args["request"]["query_params"] = query

        args["request"]["path_params"] = r.path_params

    rsp = Response()

    file = open(html, "r")
    text = file.read()
    file.close()

    # rsp.body = _convertResponse(text, args)
    rsp.body = Lexer.convertCode(text, args)
    logger.info("Created response in: " + str(Timer.stop("Response")) + "ms")
    return rsp

async def home(r):
    return createResponse(r, "pages/index.html")

async def load_script(r, script):
    res = Response(content_type="application/javascript")
    found = open("scripts/" + script + ".js")
    res.body = found.read()
    found.close()

    return res

async def load_styles(r, sheet):
    res = Response(content_type="text/css")
    found = open("styles/" + sheet + ".css")
    res.body = found.read()
    found.close()

    return res


compiled_routes = {
}

def run():
    global app, router
    # application = router + http server
    router = Router()
    router.add_routes({
        (r'/', "home"): home,
        (r'/scripts/{script}', "script"): load_script,
        (r'/styles/{sheet}', "styles"): load_styles,
    })
    router.add_routes(compiled_routes)

    Lexer.registerScript(For())
    Lexer.registerScript(Echo())
    Lexer.registerScript(Set())
    Lexer.registerScript(Route(router))

    app = App(router, port=3030)
    app.start_server()
