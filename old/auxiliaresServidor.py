# -*- coding: utf-8 -*-

#datos o funciones auxiliares para mantener ordenado nuestro codigo del servidor

import time
import numpy as np
import random
#from paho.mqtt.client import Client

def monigotes():

    """
    Función que devuelve la lista con los sucesivos
    monigotes desde el inicio hasta el fin del juego del ahorcado.
    
    Parameters
    ----------
    None.
        
    Returns
    -------
    list : lista con los sucesivos estados de los monigotes.
    
    """

    listaMonigotes = ['''

    ''', '''
   +---+
   |   |
       |
       |
       |
       |
 =========''', '''

   +---+
   |   |
   O   |
       |
       |
       |
 =========''', '''

   +---+
   |   |
   O   |
   |   |
       |
       |
 =========''', '''

   +---+
   |   |
   O   |
  /|   |
       |
       |
 =========''', '''

   +---+
   |   |
   O   |
  /|\  |
       |
       |
 =========''', '''
 
   +---+
   |   |
   O   |
  /|\  |
  /    |
       |
 =========''', '''

   +---+
   |   |
   O   |
  /|\  |
  / \  |
       |
 =========''']

    return listaMonigotes

def decidirPartidaParaJugador(jugadores, ipPuerto):

    """
    Función que, dados los jugadores conectados al juego mediante el diccionario jugadores,
    y la referencia a la conexión de un jugador concreto mediante ipPuerto,
    encuentra la posición del jugador en el diccionario y le asigna una partida según la misma.
    
    Parameters
    ----------
    jugadores : dict
        Descripción del parámetro
    ipPuerto : tuple
        Tupla con la ip y el puerto.
        
    Returns
    -------
    pos: int
        Posición del jugador en el diccionario.
    partida: int
        Partida asignada al jugador.
    
    """
    pos = np.where( [ c==ipPuerto for (c,_) in np.array( list(jugadores.items()) )] )[0][0] + 1

    if pos % 2 == 0: # la posición es par

        partida = pos/2

    else: # la posición es impar

        partida = (pos-1)/2 + 1

    return int(pos), int(partida)


def saludar(apodo, pos, jugador):
    """
    Función que, dados 3 parámetros, envía un mensaje de saludo al jugador requerido
    
    Parameters
    ----------
    apodo : string
        Nombre del usuario
    pos : int
        Número de posición del jugador en la partida
    jugador : multiprocessing.connection.Connection
        El jugador representa la conexión recibida de un jugador

    Returns
    -------
    None.
    
    """

    if pos % 2 != 0:

        mensaje = 'Hola '+apodo+' tu papel es de Jugador 1.'

    else:

        mensaje = 'Hola '+apodo+' tu papel es de Jugador 2.'

    try:

        jugador.send(mensaje)

    except IOError:

        print ('No enviado, conexión abruptamente cerrada por el jugador')


def establecerLongitudPalabra(partida, jugadores, cerrojo):
    """
    Función que, dada la partida y los jugadores involucrados en ella, introduce
    en el diccionario de los jugadores, una longitud aleatoria para la palabra a enviar.
    Ambos jugadores tendrán la misma longitud.
    
    Parameters
    ----------
    partida : int
        Partida asignada a cada jugador
    jugadores : dict
        Diccionario con la información de la partida, la IP y el puerto del jugador y su apodo
    cerrojo : multiprocessing.synchronize.Lock
        Cerrojo para controlar la concurrencia que pueda darse

    Returns
    -------
    None.

    """
    lonPalabra = random.randint(4,6)

    for (ip, lista) in jugadores.items():

            if lista[0] == partida:

                if len(lista) < 3: 

                    cerrojo.acquire()

                    jugadores[ip] = jugadores[ip] + [lonPalabra]  

                    cerrojo.release()


def notificar_inicio_juego(jugador, ipPuerto, jugadores, juegoActivo):
    """
    Fución que, dada una conexión correspondiente a un jugador, su información de IP y Puerto
    y el diccionario de los jugadores con la información necesaria para jugar cada partida, 
    envía a cada jugador la petición de introducir una palabra de la longitud anteriormente
    calculada de forma aleatoria.

    Parameters
    ----------
    jugador : multiprocessing.connection.Connection
        Conexión aceptada de un jugador
    ipPuerto : tuple
        Tupla con el número IP y el puerto del jugador
    jugadores : dict
        Diccionario con la información de cada jugador aceptado en el servidor.
    juegoActivo: tipo
        indica si el juego sigue activo o ha finalizado

    Returns
    -------
    None.

    """
    lonPalabra = jugadores[ipPuerto][2]

    try:

        jugador.send("Elige una palabra de longitud "+str(lonPalabra))

    except IOError:

        print ('No enviado, conexión abruptamente cerrada por el jugador')

        juegoActivo.value = False


def pedirPalabraOLetra(jugador, juegoActivo): 
    """
    Función que, dada una conexión aceptada a un jugador, devuelve el mensaje recibido por
    el servidor.

    Parameters
    ----------
    jugador : multiprocessing.connection.Connection
        Conexión aceptada por el servidor
    juegoActivo:
        Indica si una partida sigue o no activa

    Returns
    -------
    m : str
        Mensaje recibido por el servidor

    """
    try:

        m = jugador.recv()

        return m

    except Exception:

        print('El jugador se ha ido')

        juegoActivo.value = False


def palabracontraria(partida, jugadores, ipPuerto):
    """
    Función que, dados la partida, los jugadores y la tupla de la IP 
    y el puerto de cada jugador, devuelve la palabra que tiene que adivinar cada jugador
    en cuestión, es decir, la palabra ofrecida por el rival.

    Parameters
    ----------
    partida : int
        Número de partida que se está jugando
    jugadores : dict
        Diccionario de los jugadores en el ahorcado.
    ipPuerto : tuple
        Tupla con la IP y el puerto de los jugadores

    Returns
    -------
    palabraContr : str
        Palabra que un jugador tiene que adivinar en el ahorcado

    """
    for (ip, lista) in jugadores.items():

            if lista[0] == partida:

                if ip != ipPuerto: #si es mi contrincante y no yo

                    palabraContr = lista[3]  

                    break

    return palabraContr


def mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabraSecreta):
    """
    Función que le permite al usuario ver cómo se está desarrollando su partida.

    Parameters
    ----------
    listaMonigotes : list
        Lista de los monigotes del ahorcado
    letrasIncorrectas : list
        Lista de las letras que han sido probadas y han fallado por no hallarse en la palabra
    letrasCorrectas : list
        Lista con las letras de la palabra
    palabraSecreta : str
        Palabra que un jugador ha de adivinar
    Returns
    -------
    envio : str
        La información necesaria en string para continuar la partida

    """
    espaciosVacios = '_' * len(palabraSecreta)

    for i in range(len(palabraSecreta)): # completar los espacios vacíos con las letras adivinadas

        if palabraSecreta[i] in letrasCorrectas:

            espaciosVacios = espaciosVacios[:i] + palabraSecreta[i] + espaciosVacios[i+1:]

    envio = '\n'+listaMonigotes[len(letrasIncorrectas)]+'\n'*2+'Letras incorrectas: '+str(letrasIncorrectas)+'\n'+'Lo que llevas de la palabra: '+str(espaciosVacios)+'\n'

    return envio


def ahorcado(jugador, ipPuerto, palabra, jugadores, partida, cerrojo, pareja, pos, juegoActivo):
    """
    Esta es la función del propio juego del ahorcado. Recibiendo los parámetros indicados
    y los mensajes que le lleguen del servidor al usuario, podrá interactuar con el mismo
    para jugar al ahorcado. La partida se termina cuando uno de los jugadores ha ganado,
    cuando ambos han perdido, o cuando algo ha ido mal en las conexiones.

    Parameters
    ----------
    jugador : multiprocessing.connection.Connection
        Conexión del jugador aceptada por el servidor.
    ipPuerto : tuple
        Tupla con la IP y el puerto de cada jugador
    palabra : str
        Palabra que cada jugador ha de adivinar
    jugadores : dict
        Diccionario de los jugadores donde la clave es la IP y el puerto asignados, y el valor
        es una lista de información conel número de partida asignada, la IP, el puerto del jugador,
        la información de su Client, el apodo, y la palabra elegida por este para que su rival
        adivine
    partida : int
        Número de partida
    cerrojo : multiprocessing.synchronize.Lock
        Cerrojo para resolver los problemas de concurrencia
    pareja : numpy.ndarray
        Indica qué dos jugadores están en la misma partida
    pos : int
        Posición del jugador en la partida
    juegoActivo: 
        Indica si la partida sigue activa o ha finalizado

    Returns
    -------
    None.

    """
    listaMonigotes = monigotes()
    nTotalIntentos = len(listaMonigotes) - 1
    letrasCorrectas = []
    letrasIncorrectas = []
    nIntentosFallidos = 0

    while juegoActivo.value:

        letra = pedirPalabraOLetra(jugador, juegoActivo)

        #Si no he recibido la letra bien, juegoActivo cambia a False.

        if juegoActivo.value: #Si la he recibido bien, la coloco.

            if letra in palabra:

                letrasCorrectas.append(letra)

            else:

                letrasIncorrectas.append(letra)

        else:

            print("PARTIDA FINALIZADA POR HUÍDA DE UN JUGADOR")

            break

        #CASO 1: si el otro es ganador ya no puede seguir tampoco

        if [ lista[4]=='ganador' for (_,lista) in [list(jugadores.items())[i] for i in pareja] ][pos%2] or jugadores[ipPuerto] == jugadores[ipPuerto][0:4]+['ganador']:

            try:

                jugador.send("TU CONTRINCANTE HA GANADO")

            except IOError:

                print ('No enviado, conexión abruptamente cerrada por el jugador')

                juegoActivo.value = False

            break

        #CASO 2: si ha acertado todas las letras es ganador

        if all([char in letrasCorrectas for char in palabra]):

            cerrojo.acquire()

            jugadores[ipPuerto] = jugadores[ipPuerto][0:4]+['ganador']

            cerrojo.release()


            try:

                jugador.send("HAS GANADO, la palabra era "+palabra)

            except IOError:

                print ('No enviado, conexión abruptamente cerrada por el jugador')

                juegoActivo.value = False

            break

        #CASO 3: si ha agotado todos sus intentos

        nIntentosFallidos = len(letrasIncorrectas)

        if nIntentosFallidos == nTotalIntentos:

            cerrojo.acquire()

            jugadores[ipPuerto] = jugadores[ipPuerto][0:4]+['agotado intentos']

            cerrojo.release()

            try:

                jugador.send("HAS AGOTADO TODOS TUS INTENTOS, la palabra era "+palabra)

            except IOError:

                print ('No enviado, conexión abruptamente cerrada por el jugador')

                juegoActivo.value = False

            break

        #si ninguno de esos casos se ha dado, es que el juego continua para mí

        try:

            jugador.send( mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabra) )

        except IOError:

            print ('No enviado, conexión abruptamente cerrada por el jugador')

            juegoActivo.value = False


def borrarParejaDict(pareja, jugadores):
    """
    Función que busca borrar una pareja del juego en el diccionario de los jugadores
    cuando la partida entre ambos haya finalizado.

    Parameters
    ----------
    pareja : numpy.ndarray
        Usuarios involucrados
    jugadores : dict
        Diccionario de todos los jugadores en el ahorcado

    Returns
    -------
    None.

    """
    ipsPareja = [ ip for (ip,_) in [list(jugadores.items())[i] for i in pareja] ]

    for ip in ipsPareja:

        del jugadores[ip] # lo borro del diccionario


def on_publish(client, userdata, mid):
    """
    Función que permite publicar la información de la partida en un topic

    Parameters
    ----------
    client : TYPE
        DESCRIPTION.
    userdata : TYPE
        DESCRIPTION.
    mid : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    print("Resultado publicado.\n")


def publicarResultados(lista):
    """
    Función que permite publicar los resultados de los ganadores en la web de la asignatura

    Parameters
    ----------
    lista : list
        Lista de las partidas

    Returns
    -------
    None.

    """
    cliente = Client()

    cliente.connect("wild.mat.ucm.es")

    cliente.on_publish = on_publish

    topic = 'clients/resultadosAhorcado'

    mensaje = "RESULTADO EN LA PARTIDA "+str(lista[0])+" para el jugador con apodo "+lista[1]+": "+" Propuso la palabra "+lista[3]+" y finaliza el juego con el estado "+lista[4]+"."

    print ('Mensaje  a publicar en ', topic, ': ', mensaje)

    cliente.publish(topic,mensaje)
