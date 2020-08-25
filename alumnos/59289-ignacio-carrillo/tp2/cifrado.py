import os 

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