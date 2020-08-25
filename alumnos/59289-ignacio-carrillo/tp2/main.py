import os
import threading
import array
from concurrent import futures
from time import time
from cifrado import rot13
from parser import parser

global leido #variable global q almacena el bloque leido
barrera= threading.Barrier(4) #barrera q espera por los 4 hilos --> 3 y main. Pto de encuentro
candado= threading.Lock() #Excl mutua 


def manejo_errores(argumentos):

    if(argumentos.size) < 1:
        print("--ERROR--El tamaño del bloque de lectura debe ser positivo\n")
        exit(-1)

    try:
        fd_cont = os.open(argumentos.file, os.O_RDONLY)
    except:
        print("El archivo contenedor no existe en el directorio de trabajo\n")
        exit(-1)
    
    try:
        fd_msj = os.open(argumentos.message, os.O_RDONLY)
    except:
        print("El archivo mensaje no existe en el directorio de trabajo\n")
        exit(-1)

    if argumentos.offset<0:
        print("EL valor del offset debe ser mayor o igual a cero\n")
        exit(-1)

    if argumentos.interleave<1:
        print("El valor de interleave debe ser mayor a cero\n")

    # correcion de tamaño bloque para que sea divisible por 3, incluir todos los colores de un pixel en la lectura
    if argumentos.size % 3 != 0:
        argumentos.size += (3-(argumentos.size % 3))
    
    #devuelvo los fd abiertos de la imagen contenedora y de el mensaje 
    return fd_cont,fd_msj


def leer_mensaje(archivo, bloque):
    fd_mensaje=os.open(archivo, os.O_RDONLY)
    # creo una lista para almacenar cada caracter del estegomensaje en byte
    lista_binario = []
    while True:
        mensaje_leido = os.read(fd_mensaje, bloque)
        for i in mensaje_leido:
            lista_binario.append("{0:08b}".format(i))
        if len(mensaje_leido) != bloque:
            break

    # convierto la lista de bytes binarios en una lista de bits
    mensaje_binario = []
    for i in lista_binario:
        for j in i:
            mensaje_binario.append(j)

    os.close(fd_mensaje)
    return mensaje_binario, len(lista_binario)


def calcular_offset(bloque):
    lineas=bloque.splitlines()
    offset=0

    for linea in lineas:
        if linea==b'P6':
            offset+=len(linea)+1
        elif linea[0]==ord('#'):
            offset+=len(linea)+1
        elif len(linea.split())==2:
            offset+=len(linea)+1
        else:
            offset+=len(linea)+1
            break
    
    return offset


def modificar_header(header,linea_ad):
    header=header[:3]+linea_ad.encode()+header[2:]
    return header


def generar_imagen(indices,msj,t_bytes,indice_h):
    global leido
    escrito=0

    while escrito<t_bytes:
        escrito=len(leido)
        while indices!=[] and indices[0]<escrito: #me fijo q la lista no este vacia, y no escribir donde aun no leo
            candado.acquire()
            indice=indices.pop(0)
            leido[indice]=leido[indice][:7]+msj.pop(0) #cambio el LSB del byte correspondiente
            candado.release()
        barrera.wait()
    return indice_h


if __name__ == "__main__":
    
    start= time() #inicializo el tiempo p calcular cuanto demora

    os.system("reset") 

    # instancio el parser de argumentos
    argumentos = parser()

    # manejo errores de los argumentos anteriores y devuelvo el fd del contenedor y del msj si estos existen
    fd_imgcont,fd_msj=manejo_errores(argumentos)

    #Creo e inicializo el hilo q realiza el cifrado
    if argumentos.cifrado == True:
        hilo_cifrado=threading.Thread(target=rot13,args=(fd_msj,argumentos.size,argumentos.message))
        hilo_cifrado.start()
        hilo_cifrado.join() #Para leer el msj, debo esperar q este cifrado, asique espero al hilo cifrador

    #leer mensaje y pasar a binario, y devuelvo la long de msj en bytes
    mensaje_bin,long_msj = leer_mensaje(argumentos.message,argumentos.size)

    #armo comentario para agregar a header 
    if argumentos.cifrado == True:
        linea_header="#UMCOMPU2-C {} {} {}".format(str(argumentos.offset),str(argumentos.interleave),str(long_msj))
    else:
        linea_header="#UMCOMPU2 {} {} {}".format(str(argumentos.offset),str(argumentos.interleave),str(long_msj))
    
    #Lectura parcial de la imagen para buscar el header
    busq_header=os.read(fd_imgcont,100)
    offset=calcular_offset(busq_header)
    os.lseek(fd_imgcont,offset,0) #posiciono el offset al inicio del header para la lectura

    #Armo y escribo el nuevo header
    header=modificar_header(busq_header[:offset],linea_header)
    salida=open(argumentos.output,"wb", os.O_CREAT)
    salida.write(bytearray(header.decode(),'ascii'))

    #Testear validez del portador
    bytes_imagen=os.path.getsize(argumentos.file)
    if(len(mensaje_bin)*argumentos.interleave+offset)>(bytes_imagen-offset):
        print("El numero de bytes necesarios para el estegomensaje, son mayores que los disponibles en el portador\n")
        exit(-1)

    #Determinar posiciones del header a modificar para esconder el msj
    posiciones_raster=[]
    color=0
    for indiceR in range(argumentos.offset*3,bytes_imagen,argumentos.interleave*3):
        posiciones_raster.append(color+indiceR)
        color+=1
        if color==3:
            color=0
        if(len(posiciones_raster)==len(mensaje_bin)): #solo me interesan los indices necesarios para esconder el mensaje
            break
    
    #Separo las posiciones correspondientes a cada color RGB
    pos_r=[posiciones_raster[i] for i in range(0,len(posiciones_raster),3)]
    pos_g=[posiciones_raster[j] for j in range(1,len(posiciones_raster),3)]
    pos_b=[posiciones_raster[k] for k in range(2,len(posiciones_raster),3)]

    indices=(pos_r,pos_g,pos_b)

    #Coloco los bits del mensaje en las colas correspondientes
    msj_r=[]
    msj_g=[]
    msj_b=[]

    for i in range(0,len(mensaje_bin),3):
        msj_r.append(mensaje_bin[i])
        try:
            msj_g.append(mensaje_bin[i+1])
            msj_b.append(mensaje_bin[i+2])
        except:
            break
    
    msj=(msj_r,msj_g,msj_b)

    #inicializo la lista de lectura
    global leido
    leido=[]

    #lanzo los hilos que esconden mensaje y escriben la nueva imagen
    threads = futures.ThreadPoolExecutor()
    futuros= [threads.submit(generar_imagen,indices[i],msj[i],bytes_imagen-offset,i) for i in range(3)]

    #Lectura por bloques de la imagen contenedora
    while True:
        candado.acquire()
        bloque=os.read(fd_imgcont,argumentos.size)
        leido +=["{0:08b}".format(i) for i in bloque]
        candado.release()
        barrera.wait()
        if len(bloque)!=argumentos.size:
            break
    
    #Deshabilito el punto de encuentro 
    try:
        barrera.wait(0.1)
    except threading.BrokenBarrierError:
        pass
    

    for i in range(3):
      print("El hilo ",i+1,"ha finalizado correctamente")

    #Realizo la conversion del mensaje en binario a hexa para escribir nuevamente el header
    for i in range(len(leido)):
        leido[i]=hex(int(leido[i],2))[2:].zfill(2)
    
    raster=''
    raster+="".join(leido)
    raster=bytes.fromhex(raster)
    salida.write(raster)
    salida.close()

    #Calculo del tiempo, y mensaje de finalizacion
    print("\nEl estegomensaje ha sido creado con exito\n")
    print("Tiempo total: ",str(time()-start)[:6]," segundos\n")
    print("El tamaño del header en bytes es:",len(header),"")
    print("Longitud del msj bytes:",long_msj,"\n")
