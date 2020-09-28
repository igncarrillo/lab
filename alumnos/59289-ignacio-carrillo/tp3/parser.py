import argparse
import os

def parser():

    parser = argparse.ArgumentParser(description="TP3 - Servidor web y filtro de imagen ppm")

    parser.add_argument('-p', '--port', type=int, default=5000, required=False,
                        metavar='', help='Puerto en donde se esperan conexiones nuevas')
    parser.add_argument('-d', '--documentRoot', type=str , default="/prueba", required=False, metavar='',
                        help='Directorio donde se encuentran los documentos web')
    parser.add_argument('-s', '--size', default=1024, type=int, required=False, metavar='',
                        help='Bloque de lectura de los documentos web')

    args = parser.parse_args()

    if args.size % 3 != 0:
        args.size += (3 - (args.size % 3))

    if args.size<1:
        print("Debe ingresar un bloque de lectura valido")
        exit(-1)

    path=f"{os.getcwd()}{args.documentRoot}"

    if not os.path.exists(path):
        print("El path especificado no existe")
        exit(-1)
    else:
        os.chdir(path)

    return args