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

import re, math, json

# Make Better (Scripts)
incPtn = re.compile(r"""
({{\s*(?:for\s*([\w\d]+)\s*(-?[\d]+)\s*(-?[\d]+)\s*(-?[\d]*)\s*\[([^\]]*))\]\s*}})|
({{\s*(?:include\s*["']([\w\d\/\.]+)["'])\s*}})|
({{\s*(?:set\s*([\w\d\.]+)\s*=\s*["']([^"']+))["']\s*}})|
({%\s*([\w\d\.]+)\s*%})|
({{\s*route\s*([\w\d]+)\s*(\([^\)]+\))?\s*}})|
({{\s*(?:run\s*([\w\d]+)\.([\w\d_]+))(?:\(([^\)]*)\))?\s*}})
""".replace("\n", ""))
#/ Make Better
variablePtn = re.compile(r"""$$([^\s]+)""")
registry = {
    "Math": math
}
app = None
router = None

def _convertResponse(body, args):
    global incPtn
    ms = incPtn.findall(body)

    for m in ms:
        if m[0] != "": # For loop
            repl = m[0]
            var = m[1]
            start = int(m[2])
            end = int(m[3])
            step = int(m[4]) if m[4] != "" else 1
            code = m[5]

            compiled = ""
            for _loop in range(start, end, step):
                args[var] = str(_loop)
                compiled += _convertResponse(code, args)
            del args[var]

            body = body.replace(repl, str(compiled))
        if m[6] != "": #include
            repl = m[6]
            file = open(m[7], "r")
            include = _convertResponse(file.read(), args)
            body = body.replace(repl, str(include))
            file.close()
        elif m[8] != "": #set
            repl = m[8]
            key = m[9]
            value = m[10]
            args[key] = value
            body = body.replace(repl, "")
        elif m[11] != "": #print
            repl = m[11]
            parts = m[12].split(".")
            
            if parts[0] in args:
                text = args[parts[0]]
                del parts[0]
                
                for part in parts:
                    if type(text) is dict:
                        text = text[part]
                    else:
                        raise ValueError(part)
                body = body.replace(repl, str(text))
            else:
                logger.info(parts[0] + " does not exist")
        elif m[13] != "": #route
            repl = m[13]
            named_route = m[14]
            params = m[15][1:-1].split(";")
            ps = {}
            
            for param in params:
                sections = param.strip().split("=")
                if len(sections) == 2:
                    ps[sections[0].strip()] = sections[1].strip()
            url = router.get_path_from_name(named_route, **ps)

            body = body.replace(repl, str(url))
        elif m[16] != "": # run
            repl = m[16]
            claz = m[17]
            function = m[18]
            params = m[19]
            params = params.strip().split(",")

            for i in range(len(params)):
                param = params[i].strip()
                paramVars = variablePtn.findall(param)
                for var in paramVars:
                    splitVar = var.split("|")
                    if len(splitVar) == 1:
                        param = args[splitVar[0]]
                    elif len(splitVar) == 2:
                        param = args[splitVar[0]] + "|" + splitVar[1]

                if re.match(r"-?\d+(?:\.\d+)?\|f", param):
                    param = float(param[:-2])
                elif re.match(r"-?\d\|d", param):
                    param = int(param[:-2])
                elif param == "True":
                    param = True
                elif param == "False":
                    param = False
                
                params[i] = param
            
            ret = getattr(registry[claz], function)(*params)
            if type(ret) is float:
                if ret % 1 == 0.0:
                    ret = int(ret)
                
            body = body.replace(repl, str(ret))
            

    return body

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
    
    rsp.body = _convertResponse(text, args)
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

    app = App(router, port=3030)
    app.start_server()
