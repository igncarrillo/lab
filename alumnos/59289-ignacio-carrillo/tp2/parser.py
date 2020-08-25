import argparse

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