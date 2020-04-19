# -*- coding: utf-8 -*-

# datos o funciones auxiliares para mantener ordenado nuestro codigo del servidor

import time
import numpy as np
import random
from paho.mqtt.client import Client

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


def saludar(apodo, papel, jugador):
    """
    Función que envía un mensaje de saludo al jugador requerido.
    
    Parameters
    ----------
    apodo : string
        Nombre del usuario.
    papel : int
        Papel del jugador en la partida (1 o 2).
    jugador : Connection
        Conexión recibida de un cliente a modo de jugador.

    Returns
    -------
    None.
    """

    if papel ==  1:
        mensaje = 'Hola '+apodo+' tu papel es de Jugador 1.'
    else:
        mensaje = 'Hola '+apodo+' tu papel es de Jugador 2.'
    
    try:
        jugador.send(mensaje)
    except IOError:
        print ('No enviado, conexión abruptamente cerrada por el jugador')


def pareja(partida, jugadores):
    """
    Función que devuelve los items del diccionario jugadores
    que tienen asignados la partida indicada.
    
    Parameters
    ----------
    partida : int
        Partida que se está jugado.
    jugadores : dict
        Diccionario con la información de los jugadores.

    Returns
    -------
    Array : Items del diccionario de la partida correspondiente.
    """
    condicion = [lista[0] == partida for (_,lista) in jugadores.items()]
    vectorItems = np.array(list(jugadores.items()))
    pareja = vectorItems[condicion]
    return pareja


def contrincante(i, papel, partida, jugadores):
    """
    Función que devuelve uno de los valores del contrincante en el diccionario.
    
    Parameters
    ----------
    i : int
        Posición en la lista de valores del elemento que quiero.
    partida : int
        Partida que se está jugado.
    jugadores : dict
        Diccionario con la información de los jugadores

    Returns
    -------
    tipo dependiente : elemento de la lista de valores.
    """
    par = pareja(partida, jugadores)
    return [ lista[i] for [_,lista] in par][papel%2] 


def establecerLongitudPalabra(partida, jugadores, cerrojo):
    """
    Función que, dada la partida y los jugadores involucrados en ella, introduce
    en el diccionario de los jugadores, una longitud aleatoria para la palabra a enviar.
    Ambos jugadores tendrán la misma longitud para que haya igualdad de condiciones.
    
    Parameters
    ----------
    partida : int
        Partida asignada a cada jugador
    jugadores : dict
        Diccionario con la información de la partida, la IP y el puerto del jugador y su apodo
    cerrojo : Lock
        Cerrojo para controlar la concurrencia con el diccionario.

    Returns
    -------
    None.

    """
    lonPalabra = random.randint(4,6)

    for (ip, lista) in jugadores.items():
            if lista[0] == partida:
                if len(lista) < 3: # solo ejecuta la asignación si no se ha hecho antes
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
    jugador : Connection
        Conexión aceptada de un jugador.
    ipPuerto : tuple
        Tupla con el número IP y el puerto del jugador.
    jugadores : dict
        Diccionario con la información de cada jugador aceptado en el servidor.
    juegoActivo: Value
        Indica si el juego sigue activo o ha finalizado.

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
    jugador : Connection
        Conexión aceptada por el servidor.
    juegoActivo: Value
        Indica si una partida sigue o no activa.

    Returns
    -------
    str :
        Mensaje recibido por el servidor.
    """

    try:
        m = jugador.recv()
        return m
    except Exception:
        print('El jugador se ha ido')
        juegoActivo.value = False


def mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabraSecreta):
    """
    Función que le permite al usuario ver cómo se está desarrollando su partida.

    Parameters
    ----------
    listaMonigotes : list
        Lista de los monigotes del ahorcado.
    letrasIncorrectas : list
        Lista de las letras que han sido probadas y han fallado por no hallarse en la palabra.
    letrasCorrectas : list
        Lista con las letras de la palabra.
    palabraSecreta : str
        Palabra que un jugador ha de adivinar.
    Returns
    -------
    str :
        Resultado del intento del jugador.
    """

    espaciosVacios = '_' * len(palabraSecreta)
    for i in range(len(palabraSecreta)): # completar los espacios vacíos con las letras adivinadas
        if palabraSecreta[i] in letrasCorrectas:
            espaciosVacios = espaciosVacios[:i] + palabraSecreta[i] + espaciosVacios[i+1:]
    envio = '\n'+listaMonigotes[len(letrasIncorrectas)]+'\n'*2+'Letras incorrectas: '+str(letrasIncorrectas)+'\n'+'Lo que llevas de la palabra: '+str(espaciosVacios)+'\n'
    return envio


def ahorcado(jugador, ipPuerto, palabra, jugadores, partida, cerrojo, papel, juegoActivo):
    """
    Esta es la función del propio juego del ahorcado. Recibiendo los parámetros indicados
    y los mensajes que le lleguen del servidor al usuario, podrá interactuar con el mismo
    para jugar al ahorcado. La partida se termina cuando uno de los jugadores ha ganado,
    cuando ambos han perdido, o cuando algo ha ido mal en las conexiones.

    Parameters
    ----------
    jugador : Connection
        Conexión del jugador aceptada por el servidor.
    ipPuerto : tuple
        Tupla con la IP y el puerto de cada jugador.
    palabra : str
        Palabra que cada jugador ha de adivinar.
    jugadores : dict
        Diccionario de los jugadores con su información.
    partida : int
        Número de partida.
    cerrojo : Lock
        Cerrojo para resolver los problemas de concurrencia con el diccionario.
    papel : int
        Papel del jugador en la partida (1 o 2).
    juegoActivo: Value
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
        
        if juegoActivo.value: # si he recibido bien la letra, la coloco
            if letra in palabra:
                letrasCorrectas.append(letra)
            else:
                letrasIncorrectas.append(letra)
        else: # Si no he recibido la letra bien, juegoActivo ha cambiado a False.
            print("PARTIDA ",partida," FINALIZADA POR HUÍDA DE UN JUGADOR")
            break
        
        #CASO 1: si el contrincante es ganador, no puede seguir
        estadoContrincante = contrincante(4, papel, partida, jugadores)
        if estadoContrincante =='ganador':
            if all([char in letrasCorrectas for char in palabra]): # si casi gano en este intento
                try:
                    jugador.send("¡VAYA! La palabra era "+palabra+", pero tu contrincante ha sido más rápido.")
                    cerrojo.acquire()
                    jugadores[ipPuerto] = jugadores[ipPuerto][0:4]+['perdedor']
                    cerrojo.release()
                except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                    juegoActivo.value = False
                break
            else: #si no estaba a una letra acertada de ganar
                try:
                    jugador.send("TU CONTRINCANTE HA GANADO")
                    cerrojo.acquire()
                    jugadores[ipPuerto] = jugadores[ipPuerto][0:4]+['perdedor']
                    cerrojo.release()
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
                envio = "HAS AGOTADO TODOS TUS INTENTOS, la palabra era "+palabra +mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabra)
                jugador.send(envio)
            except IOError:
                print ('No enviado, conexión abruptamente cerrada por el jugador')
                juegoActivo.value = False
            break

        #si ninguno de esos casos se ha dado, es que el juego continua para el jugador
        try:
            jugador.send( mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabra) )
        except IOError:
            print ('No enviado, conexión abruptamente cerrada por el jugador')
            juegoActivo.value = False


def borrarParejaDict(partida, jugadores):
    """
    Función que busca borrar una pareja del juego en el diccionario de los jugadores
    cuando la partida entre ambos haya finalizado.

    Parameters
    ----------
    partida : int
        Partida cuyos jugadores se van a eliminar.
    jugadores : dict
        Diccionario de todos los jugadores en el ahorcado.

    Returns
    -------
    None.
    """

    ipsPareja = [ ip for [ip,_] in pareja(partida, jugadores) ]
    for ip in ipsPareja:
        del jugadores[ip]


def on_publish(client, userdata, mid):
    print("Resultado publicado correctamente.\n")


def publicarResultados(lista, juegoActivo):
    """
    Función que permite publicar los resultados de los jugadores en 
    el broker de la web de la asignatura.

    Parameters
    ----------
    lista : list
        Lista de los datos a publicar.

    Returns
    -------
    None.
    """

    cliente = Client()
    cliente.connect("wild.mat.ucm.es")
    cliente.on_publish = on_publish
    topic = 'clients/resultadosAhorcado'
    if juegoActivo.value:
        mensaje = "RESULTADO EN LA PARTIDA "+str(lista[0])+" para el jugador con apodo "+lista[1]+": "+" Propuso la palabra "+lista[3]+" y finaliza el juego con el estado "+lista[4]+"."
    else:
        mensaje = " PARTIDA"+str(lista[0])+"ABRUPTAMENTE FINALIZADA"
    print ('Mensaje  a publicar en ', topic, ': ', mensaje)
    cliente.publish(topic,mensaje)
