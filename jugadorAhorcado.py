"""
PRESENTACIÓN
"""

from multiprocessing.connection import Client
import time
import auxiliaresJugador as aux



if __name__ == '__main__':

    print ('intentando conectar con en el servidor para jugar al ahorcado...')
    jugador = Client(address = ('127.0.0.1', 6000), authkey = b'secret password SERVER')
    print ('Conexión aceptada')
    apodo = input('Cuál es tu apodo como jugador? ')
    jugador.send([apodo])
    print ('enviando la información de tu listener como jugador...')

    while True:
        mensaje = jugador.recv()
        print('MANDADO DESDE SERVIDOR: ', mensaje)
        if "Elige una palabra" in mensaje:
            longitud =  int( mensaje[len(mensaje)-1] ) #el último elemento del mensaje
            palabraElegida = aux.enviarPalabraParaContrincante(longitud)
            jugador.send(palabraElegida)
        if "COMIENZA EL JUEGO" in mensaje:
            break #me salgo de este primer bucle cuando puedo comenzar el juego

    #bucle para jugar al ahorcado
    letrasProbadas = []
    continuar = True
    while continuar:
        try:
            intento =  aux.obtenerIntento(letrasProbadas)
            jugador.send(intento)
            letrasProbadas.append(intento)
            respuesta = jugador.recv()
            print(respuesta)
        except:
            print('parece que ha habido algun error')
        if ("HAS GANADO" in respuesta) or ("HAS AGOTADO" in respuesta) or ("TU CONTRINCANTE" in respuesta): #en caso contrario, es que me ha mandado el monigote y no un mensaje
            continuar = False
    
    #respuesta final por parte del servidor
    while True:
        try:
            fin = jugador.recv()
            print(fin)
        except:
            print("parece que algo está fallando")
        if ("ENHORABUENA" in fin) or ("JUEGO FINALIZADO" in fin) or ("FINALMENTE" in fin): #en caso contrario, es que mi contrincante sigue jugando
            break

    #jugador.close()
    print("FIN")