import argparse
import os
import threading
import array

def parser():

    parser = argparse.ArgumentParser(
        description="TP2 - Envio de mensaje esteganografico")
    parser.add_argument('-f', '--file', type=str, required=True,
                        metavar='', help='Nombre del archivo .ppm previo')
    parser.add_argument('-m', '--message', type=str, required=True, metavar='',
                        help='Nombre del archivo .txt donde se encuentra el mensaje')
    parser.add_argument('-o', '--output', default="output.ppm", type=str,
                        required=False, metavar='', help='Nombre del archivo .ppm con estegomensaje')
    parser.add_argument('-s', '--size', default=12, type=int,
                        required=False, metavar='', help='Tamaño del bloque n de lectura')
    parser.add_argument('-e', '--offset', default=0, type=int, required=False,
                        metavar='', help='Pixel del raster a partir del cual se escribe el mensaje')
    parser.add_argument('-i', '--interleave', default=1, type=int, required=False,
                        metavar='', help='Interleave usado en el estegomensaje')
    parser.add_argument('-c', '--cifrado', default=False, type=bool,
                        required=False, metavar='', help='Mecanismo de cifrado')

    args = parser.parse_args(("-f", "dog.ppm", "-m", "mensaje.txt", "-c", " "))

    return args


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


def rot13(fd_mensaje,bloque, archivo):
    #Abro un fd para escribir el msj cifrado
    fd_escritura=os.open(archivo,os.O_WRONLY | os.O_CREAT)

    #realizo el cifrado o descrifrado del msj 
    Cifrado = ''
    while True:
        mensaje=os.read(fd_mensaje,bloque)
        for buff in mensaje:
                if (buff >= 65 and buff <= 90) or (buff >= 97 and buff <= 122):
                    if ((buff + 13 > 90 and buff + 13 <= 103) or (buff + 13 > 122 and buff + 13 <= 135)):
                        Cifrado += chr(buff - 13)
                    else:
                        Cifrado += chr(buff + 13)
                else:
                    Cifrado+=' '                    
        os.write(fd_escritura,Cifrado.encode())  #Escribo el msj y vacio el string
        Cifrado=''

        if(len(mensaje)!=bloque):
            os.close(fd_escritura)
            os.close(fd_mensaje)
            break


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


if __name__ == "__main__":

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
    os.lseek(fd_imgcont,offset,0) #posiciono el offset al inicio del raster

    #Armo y escribo el nuevo header
    header=modificar_header(busq_header[:offset],linea_header)
    salida=open(argumentos.output,"wb", os.O_CREAT)
    salida.write(bytearray(header.decode(),'ascii'))

    #Testear validez del portador
    bytes_imagen=os.path.getsize(argumentos.file)
    if(len(mensaje_bin)*argumentos.interleave+offset)>bytes_imagen:
        print("El numero de bytes necesarios para el estegomensaje, son mayores que los disponibles en el portador\n")
        exit(-1)

    #Determinar posiciones del raster a modificar para esconder el msj
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

    #Coloco los bits del mensaje en la cola correspondiente
    msj_r=[]
    msj_g=[]
    msj_b=[]

