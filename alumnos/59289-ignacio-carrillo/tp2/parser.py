import argparse
import os
import modificador

def main():
    os.system("clear")
    parser = argparse.ArgumentParser(description="TP2 - Envio de mensaje esteganografico")
    parser.add_argument('-f','--file',type=str, required=True,metavar='',help='Nombre del archivo .ppm previo')
    parser.add_argument('-m','--message',type=str, required=True,metavar='',help='Nombre del archivo .txt donde se encuentra el mensaje')
    parser.add_argument('-o','--output',default="output.ppm",type=str, required=False,metavar='',help='Nombre del archivo .ppm posterior')

    args=parser.parse_args()

    modificador.modificar_encabezado(args.file)

if __name__ == "__main__":
    main()
