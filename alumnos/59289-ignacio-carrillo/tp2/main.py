import argparse
import os


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

    # convierto la lista en una chorrera de bits
    mensaje_binario = ''
    for i in lista_binario:
        mensaje_binario += "{}".format(i)

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


def modificar_header(fd_escritura,header,linea):
    header=header[0:3]+linea.encode()+header[2:]
    os.write(fd_escritura,header)
    return header 


if __name__ == "__main__":
    os.system("reset")

    # instancio el parser de argumentos
    argumentos = parser()

    # manejo errores de los argumentos anteriores y devuelvo el fd del contenedor y del msj si estos existen
    fd_imgcont,fd_msj=manejo_errores(argumentos)

    #realizo el cifrado del msj
    #crear hilo y el main lo debe esperar a q termine para seguir
    if argumentos.cifrado == True:
        rot13(fd_msj,argumentos.size,argumentos.message) 
    #una vez q termino el hilo de cifrado

    #leer mensaje y pasar a binario, y devuelvo la long de msj en bytes
    mensaje_bin,long_msj = leer_mensaje(argumentos.message,argumentos.size)

    #armo comentario para agregar a header 
    if argumentos.cifrado == True:
        linea_header="#UMCOMPU2-C {} {} {}".format(str(argumentos.offset),str(argumentos.interleave),str(long_msj))
    else:
        linea_header="#UMCOMPU2 {} {} {}".format(str(argumentos.offset),str(argumentos.interleave),str(long_msj))

    

