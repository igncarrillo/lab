import argparse
import os 
from multiprocessing import Process,Queue 

def calcular_offset(leido):
    cant_lineas_coment=leido.count(b"\n#")
    for i in range(cant_lineas_coment): #busco todas las lineas de comentario
            comienzo_comentario = leido.find(b"\n#")+1
            fin_comentario = leido.find(b"\n", comienzo_comentario) #fin comentario

    if(cant_lineas_coment==0):
        fin_comentario=leido.find(b"\n")
    #P6/n medidas/n profundidad/n HEADER
    medidas = leido.find(b"\n", fin_comentario+1) #linea de medidas
    profundidad = leido.find(b"\n", medidas+1) #linea de profundidad
    return profundidad+1

def procesar_datos(q,id,header,escalado): #proceso los datos y genero los archivos nuevos
    
    #coloco el nombre de cada archivo, segun el numero de proceso
    if id==0:
        nombre="rojo.ppm" 
    elif id==1:
        nombre="verde.ppm"
    else:
        nombre="azul.ppm"

    fd=os.open(nombre,os.O_WRONLY | os.O_CREAT) #genero el fd de cada rgb

    while True:
            if not q.empty():
                leido=q.get() #leo el msj
                if(leido=="EOF"):
                    break #si ya lei todo el mensaje salgo del bucle
                if(type(leido)==list): #si el mensaje es una lista, la recorro y escribo en archivo. EL mensaje puede ser el header(bytes)
                    aux=""
                    for i in range(len(leido)):
                        if(type(leido[i])==int):
                            aux+=str(int(leido[i]*escalado)) #aplico el escalado para la imagen
                        else:
                            aux+=str(leido[i])
                    leido=aux.encode()
                os.write(fd,leido) #escribo en archivo
    os.close(fd) #cierrro el fd cuando completo el archivo
    print("Proceso {} termino".format(id))
    exit(0)

def generar_colas(header):
    colas=[] #Creo 3 colas p comunicacion qr,qv,qaz
    for i in range(3):
        colas.append(Queue())
        colas[i].put(header)
    return colas

def esperar_procesos(procesos):
    for i in range(3): #el padre los espera
        procesos[i].join()

def main():
    os.system("clear")
    parser = argparse.ArgumentParser(description="Lectura de imagen ppm P6")
    parser.add_argument('-f','--archivo',type=str, required=True,metavar='',help='Nombre del archivo ppm a leer')
    parser.add_argument('-n','--bloque',type=int, required=True,metavar='',help='Tamaño del bloque de lectura')
    parser.add_argument('-r','--red',default=1,type=float, required=False,metavar='',help='Escalado intensidad filtro rojo')
    parser.add_argument('-b','--blue',default=1,type=float, required=False,metavar='',help='Escalado intensidad filtro azul')
    parser.add_argument('-g','--green',default=1,type=float, required=False,metavar='',help='Escalado intensidad filtro verde')

    args=parser.parse_args()

    ##############################Manejo de errores########################################

    if(args.blue<=0 or args.red<=0 or args.green<=0):
        print("\n***ERROR***    Finalizando programa...")
        print("Los valores de escalado deben ser mayores a cero")
        exit(-1)

    if(args.bloque<=0):
        print("\n***ERROR***    Finalizando programa...")
        print("El tamaño del bloque de lectura debe ser un entero superior a cero")
        exit(-1)
        
    try:
        archivo=os.open(args.archivo,os.O_RDONLY) #abrir descriptor
    except:
        print("\n***ERROR***    Finalizando programa...")
        print("El archivo especificado no existe en el directorio")
        exit(-1)
    
    ########################################################################################

    tamaño_header=100 #defino un tamaño aproximado para el header, puede ser tan grande como quiera. Pero disminuye rendimiento
    leido=os.read(archivo,tamaño_header) #lectura bloque busqueda header
    offset=calcular_offset(leido) #calculo del offset para raster
    header=leido[:offset]
    header=header.replace(b'P6',b'P3')
    os.lseek(archivo,offset,0) #posicionamiento de offset en fd

    colas=generar_colas(header)

    procesos=[] #Creo 3 hijos, uno por cada color
    for i in range(3):
        if(i==0):
            escalado=args.red
        elif(i==1):
            escalado=args.green
        else:
            escalado=args.blue

        procesos.append(Process(target=procesar_datos,args=(colas[i],i,header,escalado)))
        procesos[i].start()

    #leo el archivo completo
    idq=0
    while True:
        leido=os.read(archivo,args.bloque)
        if(len(leido)!=args.bloque):
            for i in leido:
                if idq==0:
                    colas[idq].put([i," "," 0"," ","0"," "]) #envio los mensajes a cada cola
                elif idq==1:
                    colas[idq].put(["0"," ",i," ","0"," "]) #envio los mensajes a cada cola
                else:
                    colas[idq].put(["0"," "," 0"," ",i," "]) #envio los mensajes a cada cola
                idq+=1
                if idq==3:
                    idq=0
            for idq in range(3):
                colas[idq].put("EOF") #avisa que termino de escribir en c cola 
            os.close(archivo) #cierra el fd del archivo leido
            print("Padre termino de escribir en las colas")
            break
        else:
            for i in leido:
                if idq==0:
                    colas[idq].put([i," "," 0"," ","0"," "]) #envio los mensajes a cada cola
                elif idq==1:
                    colas[idq].put(["0"," ",i," ","0"," "]) #envio los mensajes a cada cola
                else:
                    colas[idq].put(["0"," "," 0"," ",i," "]) #envio los mensajes a cada cola
                idq+=1
                if idq==3:
                    idq=0

    esperar_procesos(procesos)
    print("El padre termino con exito")

if __name__ == "__main__":
    main()