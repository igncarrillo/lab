import argparse

def parser():

    parser = argparse.ArgumentParser(description="TP3 - Servidor web y filtro de imagen ppm")

    parser.add_argument('-p', '--port', type=int, default=5000, required=False,
                        metavar='', help='Puerto en donde se esperan conexiones nuevas')
    parser.add_argument('-d', '--document-root', type=str , default="/index.html", required=False, metavar='',
                        help='Directorio donde se encuentran los documentos web')
    parser.add_argument('-s', '--size', default=1024, type=int, required=False, metavar='',
                        help='Bloque de lectura de los documentos web')

    args = parser.parse_args()

    return args