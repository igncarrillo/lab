import asyncio
import socket
from parser import parser
import datetime as dt
import os
from os import scandir

global abspath

async def handler(reader, writer):
    address = writer.get_extra_info('peername')
    asyncio.create_task(generar_logs(address[0],address[1]))

    lec = (await reader.read(args.size)).decode()
    if "GET" in lec:
        required = lec.split(" ")[1]
        path = os.getcwd()
        if required == "/":
            path = f"{abspath}/html/index.html"
        else:
            path = f"{path}{required}"
        path, header= generateHeader(path)
        writer.write(header)
        fdr=os.open(path,os.O_RDONLY)
        while True:
            body=os.read(fdr,args.size)
            writer.write(body)
            if(len(body)!=args.size):
                break
        await writer.drain()
        writer.close()
        await writer.wait_closed()

async def generar_logs(ip,port):
    time=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro="| Cliente: {} | Puerto: {} | Fecha: {} |\n".format(ip,port,time)
    with open(f"{abspath}/log/log.txt","a") as file:
        file.write(registro)
    file.close()

def generateHeader(path):
    mime={"jpg":"image/jpeg","pdf":"application/pdf","html":"text/html","ppm": "image/x-portable-pixmap"}
    if os.path.exists(path):
            try:
                extension = path.split(".")[1]
                extension=mime[extension]
                fline = "HTTP/1.1 200 OK"
            except KeyError:
                fline="HTTP/1.1 500 Internal Server Error"
                path=f"{abspath}/html/error500.html"
    else:
        path=f"{abspath}/html/error.html"
        fline ="HTTP/1.1 404 Not Found"
    extension=path.split(".")[1]
    size=os.stat(path).st_size
    header="{}\r\nContent-type: {}\r\nContent-lenght: {}\r\n\r\n".format(fline,mime[extension],size)
    header=bytearray(header,"utf8")

    return path, header

async def server(host,port):
    server = await asyncio.start_server(handler,host,port,family=socket.AF_UNSPEC)
    async with server:
        await server.serve_forever()

def generar_index():
    html="<!DOCTYPE html>\n<html>\n<head><meta charset=\"UTF-8\">\n<title>Index</title>\n</head>\n<body>\n"
    html+="<h2>Bienvenido a comp2</h2>\n"
    path=os.getcwd()
    archivos=[obj.name for obj in scandir(path) if obj.is_file()]
    for archivo in archivos:
        if not ".py" in archivo:
            html+="<li><a href=\"{}\">{}</a></li>\n".format(archivo,archivo)
    html+="</body>\n</html>"
    file=open(f"{abspath}/html/index.html","w")
    file.write(html)
    file.close()

if __name__ == "__main__":
    abspath=os.getcwd()
    args=parser()
    generar_index()
    asyncio.run(server(["127.0.0.1","::1"],args.port))