from aiohttp import web
import os
from parser import parser
from os import scandir
routes = web.RouteTableDef()

global abspath

@routes.get('/')
async def hello(request):
    return web.FileResponse(f"/{abspath}/html/index.html")

def generar_index(path):
    html="<!DOCTYPE html>\n<html>\n<head><meta charset=\"UTF-8\">\n<title>Index</title>\n</head>\n<body>\n"
    html+="<h2>Bienvenido a comp2</h2>\n"
    archivos=[obj.name for obj in scandir(path) if obj.is_file()]
    for archivo in archivos:
        if not ".py" in archivo:
            html+="<li><a href=\"{}\">{}</a></li>\n".format(archivo,archivo)
    html+="</body>\n</html>"
    file=open(f"{abspath}/html/index.html","w")
    file.write(html)
    file.close()

abspath=os.getcwd()
args=parser()
path=os.getcwd()
generar_index(path)
app = web.Application()
app.add_routes(routes)
app.router.add_static("/", "./")
web.run_app(app, host=["127.0.0.1", "::1"], port=args.port)

