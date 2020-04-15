# -*- coding: utf-8 -*-
"""
Este juego, ha sido creado por: Nuria Gómez Vargas, Verónica Miranda Alcázar, Judith Villamayor
Romero, Pedro José Mendoza Moreno, María Cristina Sánchez Timón y Beatriz Roca González.
Se trata del juego del ahorcado, y este archivo recoge las funciones que utiliza el
servidor del juego para poner en contacto a los diversos jugadores a los que va aceptando.
El servidor genera una partida nueva por cada dos conexiones, cada conexión que acepta
se las va pasando a un proceso que gestiona la partida.
El juego se desarrolla de la siguiente forma:
    Primero se recoge toda la información necesaria de cada jugador para comenzar una partida
    y se le pide que proponga una palabra para que su rival la adivine jugando al ahorcado, es
    decir, los jugadores irán intentando adivinar las letras que se encuentran en
    la palabra ofrecida por el rival. El servidor será el encargado de mostrarle al usuario
    cómo se va desarrollando su partida, la palabra con los huecos rellenos, las letras que 
    ya ha probado incorrectamente, como el dibujo del ahorcado correspondiente.
    Se va desarrollando el juego hasta que uno de los dos acierte o hasta que ambos hayan
    agotado todos los intentos, es decir, que hayan obtenido el monigote del
    ahorcado completo.
"""

# importación de las librerías necesarias
from multiprocessing.connection import Listener, AuthenticationError
from multiprocessing import Process, Lock, Manager, Value
import random
import time
import numpy as np
import auxiliaresServidor as aux


def serve_client(jugador, ipPuerto, jugadores, cerrojo, juegoActivo, jugadoresFinalizados):
    """
    Función esencial del servidor. Es la encargada de llevar la partida para el jugador.

    Parameters
    ----------
    jugador : connection
        Conexión de un jugador aceptada en la función principal.
    ipPuerto : tuple
        Tupla con la información IP y puerto de un jugador.
    jugadores : dict
        Diccionario con toda la información de los jugadores necesaria para la partida.
    cerrojo : Lock
        Cerrojo para resolver problemas de concurrencia con el diccionario.
    juegoActivo: Value
        Valor compartido booleano que indica si una partida sigue activa.
    jugadoresFinalizados: Value 
        Valor compartido entero que indica el número de jugadores de la partida finalizados.

    Returns
    -------
    None.
    """

    partida, apodo = jugadores[ipPuerto]

    # el papel de un jugador (1 o 2) será la posición que ocupe su ip en los elementos
    # del diccionario con la misma partida asignada
    pareja = list( filter(lambda par: par[1][0] == partida, list(jugadores.items())) )
    papel = pareja.index( (ipPuerto, jugadores[ipPuerto]) ) + 1

    # saludo a los jugadores indicando su papel
    aux.saludar(apodo, papel, jugador)

    if juegoActivo.value:

        # espero a que haya 2 jugadores asignados a la misma partida para empezar
        while True:

            if sum( [lista[0]==partida for (_,lista) in jugadores.items()] ) != 2:
                try:
                    jugador.send('Esperando al segundo jugador...')
                    time.sleep(3)
                except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                    juegoActivo.value = False
                    break
            else:
                apodoContrincante = aux.contrincante(1, papel, partida, jugadores)
                try:
                    jugador.send('Ya sois dos jugadores. Juegas contra '+ apodoContrincante+', empieza la partida...')
                except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                    juegoActivo.value = False
                break
    
    # establezco una longitud aleatoria para la palabra
    aux.establecerLongitudPalabra(partida, jugadores, cerrojo)

    if juegoActivo.value:

        # comunico la longitud establecida
        aux.notificar_inicio_juego(jugador, ipPuerto, jugadores, juegoActivo)

    if juegoActivo.value:

        # recibo la palabra
        palabra = aux.pedirPalabraOLetra(jugador, juegoActivo)     

    if juegoActivo.value:

        # coloco la palabra en la lista del jugador en el diccionario    
        cerrojo.acquire()
        jugadores[ipPuerto] = jugadores[ipPuerto] + [palabra]    
        cerrojo.release()

    if juegoActivo.value:

        # no permito continuar hasta que los 2 jugadores tienen la palabra colocada
        while True:
            par = aux.pareja(partida, jugadores)
            nJugadoresConPalabraColocada = sum( [len(lista)>=4 for [_,lista] in par] )
            if nJugadoresConPalabraColocada == 2:
                break
            else:
                try:
                    jugador.send("Espera porque tu compi todavía no ha elegido la palabra para ti...")
                    time.sleep(2)
                except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                    juegoActivo.value = False

    if juegoActivo.value:
        
        # establezco estado inicial de "sigue probando" para cada jugador de la partida en su lista
        for (ip, lista) in jugadores.items():
                if lista[0] == partida:
                    if len(lista) < 5:
                        cerrojo.acquire()
                        jugadores[ip] = jugadores[ip] + ['sigue probando']  
                        cerrojo.release()

        # establezco ya también la palabra contraria pues empieza el juego del ahorcado
        palabraContr = aux.contrincante(3, papel, partida, jugadores)
        try:
            jugador.send('COMIENZA EL JUEGO DEL  A H O R C A D O')
        except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                    juegoActivo.value = False

    if juegoActivo.value:
        
        # juego
        aux.ahorcado(jugador, ipPuerto, palabraContr, jugadores, partida, cerrojo, papel, juegoActivo)

    if juegoActivo.value:

        #el servidor manda un mensaje final
        if jugadores[ipPuerto][4] == 'ganador':
            try:
                jugador.send("ENHORABUENA")
            except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                    juegoActivo.value = False
        if jugadores[ipPuerto][4] == 'perdedor':
            try:
                jugador.send("JUEGO FINALIZADO")
            except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                    juegoActivo.value = False
        if jugadores[ipPuerto][4] == 'agotado intentos': # mi contrincante tiene oportunidad de ganar todavia
            while True:
                estadoContrincante = aux.contrincante(4, papel, partida, jugadores)
                if estadoContrincante == 'ganador':
                    try:
                        jugador.send("FINALMENTE TU CONTRINCANTE HA GANADO LA PARTIDA")
                    except IOError:
                        print ('No enviado, conexión abruptamente cerrada por el jugador')
                        juegoActivo.value = False
                    break
                elif estadoContrincante == 'agotado intentos':
                    try:
                        jugador.send("FINALMENTE NINGUNO DE LOS DOS HABEIS GANADO LA PARTIDA")
                    except IOError:
                        print ('No enviado, conexión abruptamente cerrada por el jugador')
                        juegoActivo.value = False
                    break
                else: #mi contrincante sigue con el estado 'sigue probando'
                    try:
                        jugador.send("espera a ver qué pasa con tu contrincante...")
                        time.sleep(2)
                    except IOError:
                        print ('No enviado, conexión abruptamente cerrada por el jugador')
                        juegoActivo.value = False

    if not juegoActivo.value:

        print("PARTIDA ", partida, " ABRUPTAMENTE FINALIZADA POR ALGÚN JUGADOR")
        try:
            jugador.send('SENTIMOS COMUNICAR QUE SU COMPAÑERO HA FINALIZADO ABRUPTAMENTE LA PARTIDA Y NO PUEDE CONTINUAR')
        except IOError:
            print("El mensaje no se ha mandado porque ese jugador es el que habia cerrado la partida")

    jugador.close()
    jugadoresFinalizados.value += 1
    
    # se publica el resultado para el jugador en concreto
    Process(target = aux.publicarResultados, args = ( jugadores[ipPuerto].copy(),)).start()

    # hago borrado de la pareja en el diccionario
    if jugadoresFinalizados.value == 2:
        cerrojo.acquire()
        aux.borrarParejaDict(partida, jugadores)
        cerrojo.release()



if __name__ == '__main__':

    servidor = Listener(address=('127.0.0.1', 6000), authkey=b'secret password SERVER')
    print ('Iniciando servidor del ahorcado...')

    manager = Manager()
    jugadores = manager.dict()
    cerrojo = Lock()

    partida = 0
    while True:

        partida += 1
        print("Configurando una nueva partida...")
        print("PARTIDA ", str(partida))

        juegoActivo = manager.Value("c_bool", True)
        jugadoresFinalizados = manager.Value("i",0)

        for _ in range(2):

            print ('Aceptando jugadores...')
            try:
                jugador = servidor.accept()
                ipPuerto = servidor.last_accepted                
                print ('Jugador aceptado desde la IP y puerto siguientes: ', ipPuerto)
                try:
                    infoApodoJugador = jugador.recv()
                    jugadores[ipPuerto] = [partida, infoApodoJugador]
                except EOFError:
                    print('No recibido, conexión abruptamente cerrada por el jugador')

                p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo, juegoActivo, jugadoresFinalizados))
                p.start()

            except AuthenticationError:
                print ('Conexión rechaza, contraseña incorrecta')


    servidor.close()
    print ('FIN')
    