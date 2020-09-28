import socketserver
import os
from parser import parser
import math
from filter import *

class Handler(socketserver.BaseRequestHandler):

    def analyzer(self, rules):
        if "GET" in rules:
            required=rules.split(" ")[1]
            path=os.getcwd()
            if required =="/":
                path=f"{path}/index.html"
            else:
                path=f"{path}{required}"

            self.repairSize()

            if  ".ppm?" in path:
                filter, intensity = self.queryAnalizer(path)
                if "dog.ppm?" in path:
                    path=f"{os.getcwd()}/dog.ppm"
                else:
                    path = f"{os.getcwd()}/yacht.ppm"
                fdr=os.open(path,os.O_RDONLY)
                search=os.read(fdr,1024)
                offset=self.offsetAnalyzer(search)
                os.lseek(fdr,offset,0)
                header_ppm=search[:offset]
                data=self.generateData(filter,intensity,fdr)
                data=header_ppm+data
                path, header = self.generateHeader(path)
                to_send = header + data
                self.request.sendall(to_send)
                # threads_quantity=math.ceil(((os.stat(path).st_size-offset)-offset)/arguments.size)
                # #os.lseek(fdr,offset+indiceHILO*argumento.size,0)
            else:
                path,header= self.generateHeader(path)
                self.writeData(path,header)

    def generateData(self,fltr,intensity,fdr):
        data=b""
        while True:
            leido=os.read(fdr,arguments.size)
            leido=[byte for byte in leido]
            if fltr=="R":
                for i in range(0,len(leido)-2,3):
                    leido[i]=int(leido[i]*(intensity/100))
                    if leido[i]>255:
                        leido[i]=255
                    leido[i+1]=0
                    leido[i+2]=0
            elif fltr=="G":
                for i in range(1,len(leido)-1,3):
                    leido[i]=int(leido[i]*(intensity/100))
                    if leido[i]>255:
                        leido[i]=255
                    leido[i-1]=0
                    leido[i+1]=0
            elif fltr=="B":
                for i in range(2,len(leido),3):
                    leido[i]=int(leido[i]*(intensity/100))
                    if leido[i]>255:
                        leido[i]=255
                    leido[i-1]=0
                    leido[i-2]=0
            elif fltr=="W":
                for i in range(0,len(leido)-2,3):
                    prom=int((leido[i]+leido[i+1]+leido[i+2])/3)
                    leido[i]=leido[i+1]=leido[i+2]=prom
                    leido[i]=int(leido[i]*(intensity/100))
                    if leido[i]>255:
                        leido[i]=255
                    leido[i+2]=leido[i+1]=leido[i]
            else:
                for i in range(0,len(leido),1):
                    leido[i]=int(leido[i]*(intensity/100))
                    if leido[i]>255:
                        leido[i]=255
            data+=bytes(leido)
            if (len(leido)!=arguments.size):
                break
        return  data

    def offsetAnalyzer(self, block):
        lines = block.splitlines()
        offset = 0

        for line in lines:
            if line == b'P6':
                offset += len(line) + 1
            elif line[0] == ord('#'):
                offset += len(line) + 1
            elif len(line.split()) == 2:
                offset += len(line) + 1
            else:
                offset += len(line) + 1
                break

        return offset

    def writeData(self,path, header):
        try:
            fdr = os.open(path, os.O_RDONLY)
            first_it = True
            while True:
                body = os.read(fdr, arguments.size)
                to_send = body
                if first_it:
                    to_send = header + body
                    first_it = False
                self.request.sendall(to_send)
                if (len(body) != arguments.size):
                    os.close(fdr)
                    break

        except IOError:
            print("Error al abrir el archivo")

    def queryAnalizer(self,path):
        val_dict={}
        querys=(path.split("?")[1]).split("&")
        values=[value.split("=") for value in querys]
        for i in range(len(values)):
            val_dict[values[i][0]]=values[i][1]

        return val_dict["filter"],int(val_dict["Intensity"])

    def generateHeader(self,path):
        mime={"jpg":"image/jpeg","pdf":"application/pdf","html":"text/html","ppm": "image/x-portable-pixmap"}
        if os.path.exists(path):
            fline="HTTP/1.1 200 OK"
        else:
            path=f"{os.getcwd()}/error.html"
            fline ="HTTP/1.1 404 Not Found"
        extension=path.split(".")[1]
        size=os.stat(path).st_size
        header="{}\r\nContent-type: {}\r\nContent-lenght: {}\r\n\r\n".format(fline,mime[extension],size)
        header=bytearray(header,"utf8")
        return path,header

    def handle(self):
        print("Conexion establecida con el cliente {}".format(self.client_address))
        self.data = self.request.recv(1024).decode()
        self.rules=self.data.splitlines()[0]
        self.analyzer(self.rules)
        print("Cliente {} desconectado".format(self.client_address))

    def repairSize(self):
        if arguments.size % 3 != 0:
            arguments.size += (3 - (arguments.size % 3))

if __name__ == '__main__':
    os.system("reset")
    arguments=parser()
    print("Iniciando server ...")
    socketserver.ForkingTCPServer.allow_reuse_address = True
    HOST, PORT = 'localhost', arguments.port
    with socketserver.ForkingTCPServer((HOST, PORT), Handler) as server:
        server.serve_forever()

