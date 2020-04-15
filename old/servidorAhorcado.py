# -*- coding: utf-8 -*-
"""
Este juego, ha sido creado por: Nuria Gómez Vargas,Verónica Miranda Alcázar, Judith Villamayor
Romero, Pedro José Mendoza Moreno, María Cristina Sánchez Timón y Beatriz Roca González
Se trata del juego del ahorcado, y este archivo recoge las funciones que utiliza el
servidor del juego para poner en contacto a los diversos jugadores a los que va aceptando.
El servidor acepta todas las conexiones válidas, y, cada dos jugadores conectados, comienza
una partida mediante la función serve_client.
El juego se desarrolla de la siguiente forma:
    Primero se recoge toda la información necesaria de cada jugador para comenzar una partida
    y se le pide que proponga una palabra para que su rival la adivine jugando al ahorcado, es
    decir, los jugadores irán probando letra a letra adivinar las letras que se encuentran en
    la palabra ofrecida por el rival. Si esta letra se ecuentra en la palabra secreta, el 
    servidor será el encargado de mostrarle al usuario cómo se va desarrollando su partida,
    tanto por la palabra acertada con los huecos correspondientes a las letras que aún no ha
    encontrado, como las letras que ya ha probado incorrectamente, como el dibujo del 
    ahorcado correspondiente al estado actual de su partida.
    Se va desarrollando el juego hasta que uno de los dos acierte o hasta que ambos hayan
    agotado todos los intentos, es decir, que hayan obtenido el monigote del
    ahorcado completo.
"""

from multiprocessing.connection import Listener, AuthenticationError
from multiprocessing import Process, Lock, Manager, Value
import random
import time
import numpy as np
import auxiliaresServidor as aux


def serve_client(jugador, ipPuerto, jugadores, cerrojo, juegoActivo, jugadoresFinalizados):

    """
    Función esencial del servidor. Es la encargada de llevar la partida entre dos jugadores.

    Parameters
    ----------
    jugador : connection
        Conexión de un jugador aceptada en la función principal
    ipPuerto : tuple
        Tupla con la información IP y puerto de un jugador
    jugadores : dict
        Diccionario con toda la información de los jugadores necesaria para la partida
    cerrojo : multiprocessing.synchronize.Lock
        Cerrojo para resolver posibles problemas de concurrencia.
    juegoActivo:
        Indica si una partida sigue activa
    jugadoresFinalizados:
        Indica si los jugadores han acabado la partida

    Returns
    -------
    None.

    """

    #asigno una partida al jugador:

    pos, partida = aux.decidirPartidaParaJugador(jugadores, ipPuerto)

    apodo = jugadores[ipPuerto][0] 

    
    cerrojo.acquire()

    jugadores[ipPuerto] = [partida] + jugadores[ipPuerto] 

    cerrojo.release()

    aux.saludar(apodo, pos, jugador)

    if juegoActivo.value:

        #espero a que haya dos jugadores asignados a la misma partida para empezar

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

                pareja = np.where( [lista[0]==partida for (_,lista) in jugadores.items()] )[0]

                apodoContrincante = [ lista[1] for (_,lista) in [list(jugadores.items())[i] for i in pareja] ][pos%2]

                try:

                    jugador.send('Ya sois dos jugadores. Juegas contra '+ apodoContrincante+', empieza la partida...')

                except IOError:

                    print ('No enviado, conexión abruptamente cerrada por el jugador')

                    juegoActivo.value = False

                break

    aux.establecerLongitudPalabra(partida, jugadores, cerrojo)

    if juegoActivo.value:

        #comunico la longitud establecida

        aux.notificar_inicio_juego(jugador, ipPuerto, jugadores, juegoActivo)

    if juegoActivo.value:

        #recibo la palabra

        palabra = aux.pedirPalabraOLetra(jugador, juegoActivo)     

    if juegoActivo.value:

        #coloco la palabra en la lista del jugador en el diccionario    

        cerrojo.acquire()

        jugadores[ipPuerto] = jugadores[ipPuerto] + [palabra]    

        cerrojo.release()

    if juegoActivo.value:

        #bucle que no permita continuar hasta que los 2 jugadores tienen la palabra colocada

        while True:

            nJugadoresConPalabraColocada = sum( [len(lista)>=4 for (_,lista) in [list(jugadores.items())[i] for i in pareja]] )

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
        
        #establezco estado de SIGUE PROBANDO para cada jugador de la partida en su lista

        #este estado pasará a ser GANADOR si gana o AGOTADO INTENTOS si se ahorca

        for (ip, lista) in jugadores.items():

                if lista[0] == partida:

                    if len(lista) < 5:

                        cerrojo.acquire()

                        jugadores[ip] = jugadores[ip] + ['sigue probando']  

                        cerrojo.release()

        
        #establezco ya también la palabra contraria pues empieza el juego del ahorcado

        palabraContr = aux.palabracontraria(partida, jugadores, ipPuerto)

        try:

            jugador.send('COMIENZA EL JUEGO DEL  A H O R C A D O')

        except IOError:

                    print ('No enviado, conexión abruptamente cerrada por el jugador')

                    juegoActivo.value = False

    if juegoActivo.value:

        aux.ahorcado(jugador, ipPuerto, palabraContr, jugadores, partida, cerrojo, pareja, pos, juegoActivo)

    if juegoActivo.value:

        if jugadores[ipPuerto][4] == 'ganador':

            try:

                jugador.send("ENHORABUENA")

            except IOError:

                    print ('No enviado, conexión abruptamente cerrada por el jugador')

                    juegoActivo.value = False

        if jugadores[ipPuerto][4] == 'sigue probando':

            try:

                jugador.send("JUEGO FINALIZADO")

            except IOError:

                    print ('No enviado, conexión abruptamente cerrada por el jugador')

                    juegoActivo.value = False

        if jugadores[ipPuerto][4] == 'agotado intentos': # mi contrincante tiene oportunidad de ganar todavia

            #establezco la ip de mi contrincante:

            for (ip,_) in [list(jugadores.items())[i] for i in pareja]:

                if ip != ipPuerto: #la ip es la de mi contrincante, no la mía

                    contrincante = ip

                    break

            while True:

                if jugadores[contrincante][4] == 'ganador':

                    try:

                        jugador.send("FINALMENTE TU CONTRINCANTE HA GANADO LA PARTIDA")

                    except IOError:

                        print ('No enviado, conexión abruptamente cerrada por el jugador')

                        juegoActivo.value = False

                    break

                elif jugadores[contrincante][4] == 'agotado intentos':

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

        print("PARTIDA ABRUPTAMENTE FINALIZADA POR ALGÚN JUGADOR")

        try:

            jugador.send('SENTIMOS COMUNICAR QUE SU COMPAÑERO HA FINALIZADO ABRUPTAMENTE LA PARTIDA Y NO PUEDE CONTINUAR')

        except IOError:

            print("El mensaje no se ha mandado porque ese jugador es el que habia cerrado la partida")

    jugador.close()

    jugadoresFinalizados.value += 1

    print("JUGADORES QUE HAN FINALIZADO:" ,jugadoresFinalizados.value)

    Process(target = aux.publicarResultados, args = ( jugadores[ipPuerto].copy(),)).start()


    if jugadoresFinalizados.value == 2:

        cerrojo.acquire()

        aux.borrarParejaDict(pareja, jugadores)

        cerrojo.release()

        print("JUGADORES BORRADOS")

    print(jugadores)


if __name__ == '__main__':



    servidor = Listener(address=('127.0.0.1', 6000), authkey=b'secret password SERVER')

    print ('Iniciando servidor del ahorcado...')

    

    manager = Manager()

    jugadores = manager.dict()

    cerrojo = Lock()



    while True:

        print("Configurando una nueva partida...")



        juegoActivo = manager.Value("c_bool", True)

        jugadoresFinalizados = manager.Value("i",0)

        #print(juegoActivo.value)

        for _ in range(2):

            print ('Aceptando jugadores...')

            try:

                jugador = servidor.accept()

                ipPuerto = servidor.last_accepted                

                print ('Jugador aceptado desde la IP y puerto siguientes: ', ipPuerto)

                

                try:

                    infoApodoJugador = jugador.recv()

                    jugadores[ipPuerto] = infoApodoJugador

                except EOFError:

                    print('No recibido, conexión abruptamente cerrada por el jugador')

                

                p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo, juegoActivo, jugadoresFinalizados))

                p.start()



            except AuthenticationError:

                print ('Conexión rechaza, contraseña incorrecta')





    servidor.close()

    print ('FIN')