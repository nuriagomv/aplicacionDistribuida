# -*- coding: utf-8 -*-
"""
En este archivo, tenemos las funciones necesarias para el desarrollo del juego del
ahorcado desde el punto de vista del usuario que juega desde su casa.
El cliente se intentará conectar al servidor del ahorcado, y cuando este sea aceptado 
y en la partida asignada sean ya dos jugadores, comenzará la partida entre ambos mediante
los diversos mensajes enviados y recibidos entre el servidor y los clientes.
Una partida terminará cuando ambos hayan agotado sus intentos o uno de los dos haya encontrado
la palabra antes que el otro. También se recogen algunos posibles errores que puedan darse con
la conexión.
Para hacer un código más corto, hemos importado varias funciones de distintos archivos que 
permiten que todo se resuelva sin problemas.

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

    pasoSiguiente = True

    while continuar:

        intento =  aux.obtenerIntento(letrasProbadas)

        jugador.send(intento)

        letrasProbadas.append(intento)

        try:

            respuesta = jugador.recv()

            print(respuesta)

        except EOFError:

            print('parece que ha habido algun error')

        if ("HAS GANADO" in respuesta) or ("HAS AGOTADO" in respuesta) or ("TU CONTRINCANTE" in respuesta): #en caso contrario, es que me ha mandado el monigote y no un mensaje

            continuar = False

        if ("SENTIMOS COMUNICAR" in respuesta):

            continuar = False

            pasoSiguiente = False

    #respuesta final por parte del servidor

    while pasoSiguiente:

        try:

            fin = jugador.recv()

            print(fin)

        except EOFError:

            print("parece que algo está fallando")

        if ("ENHORABUENA" in fin) or ("JUEGO FINALIZADO" in fin) or ("FINALMENTE" in fin): #en caso contrario, es que mi contrincante sigue jugando

            break

    print("FIN")

    jugador.close()