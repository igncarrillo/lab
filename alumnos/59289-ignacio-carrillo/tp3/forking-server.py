import socketserver
import os
from parser import parser

class Handler(socketserver.BaseRequestHandler):

    def analyzer(self, rules):
        if "GET" in rules:
            required=rules.split(" ")[1]
            path=os.getcwd()
            if required =="/":
                path=f"{path}/index.html"
            elif required=="/dog.ppm":
                path=f"{path}/selector.html"
            else:
                path=f"{path}{required}"

            path,header=self.generateHeader(path)

            try:
                fdr=os.open(path,os.O_RDONLY)
                first_it=True
                while True:
                    body=os.read(fdr,arguments.size)
                    to_send=body
                    if first_it:
                        to_send = header + body
                        first_it=False
                    self.request.sendall(to_send)
                    if (len(body)!=arguments.size):
                        os.close(fdr)
                        break
            except IOError:
                print("Error al abrir el archivo")

    def generateHeader(self,path):
        mime={"jpg":"image/jpeg","pdf":"application/pdf","html":"text/html","ppm": "image/x-portable-pixmap"}
        if os.path.exists(path):
            fline="HTTP/1.1 200 OK"
        else:
            path=f"{os.getcwd()}/error.html"
            fline ="HTTP/1.1 400 File not found"
        extension=path.split(".")[1]
        size=os.stat(path).st_size
        header="{}\r\nContent-type: {}\r\nContent-lenght: {}\r\n\r\n".format(fline,mime[extension],size)
        header=bytearray(header,"utf8")
        return path,header

    def handle(self):
        print("Conexion establecida con el cliente")
        self.data = self.request.recv(1024).decode()
        self.rules=self.data.splitlines()[0]
        self.analyzer(self.rules)
        print("Cliente desconectado")

if __name__ == '__main__':
    os.system("reset")
    arguments=parser()
    print("Iniciando server...")
    socketserver.ForkingTCPServer.allow_reuse_address = True
    HOST, PORT = 'localhost', 5000
    with socketserver.ForkingTCPServer((HOST, PORT), Handler) as server:
        server.serve_forever()

