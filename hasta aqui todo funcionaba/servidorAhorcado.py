"""
PRESENTACIÓN
"""

from multiprocessing.connection import Listener, AuthenticationError
from multiprocessing import Process, Lock, Manager
import random
import time
import numpy as np
import auxiliaresServidor as aux


def serve_client(jugador, ipPuerto, jugadores, cerrojo):

    #asigno una partida al jugador:
    pos, partida = aux.decidirPartidaParaJugador(jugadores, ipPuerto)
    apodo = jugadores[ipPuerto][0] 
    
    cerrojo.acquire()
    jugadores[ipPuerto] = [partida] + jugadores[ipPuerto] 
    cerrojo.release()

    aux.saludar(apodo, pos, jugador)

    #espero a que haya dos jugadores asignados a la misma partida para empezar
    while True:
        if sum( [lista[0]==partida for (_,lista) in jugadores.items()] ) != 2:
            try:
                jugador.send('Esperando al segundo jugador...')
            except IOError:
                print ('No enviado, conexión abruptamente cerrada por el jugador')
            time.sleep(3)
        else:
            pareja = np.where( [lista[0]==partida for (_,lista) in jugadores.items()] )[0]
            apodoContrincante = [ lista[1] for (_,lista) in [list(jugadores.items())[i] for i in pareja] ][pos%2]
            try:
                jugador.send('Ya sois dos jugadores. Juegas contra '+ apodoContrincante+', empieza la partida...')
            except IOError:
                print ('No enviado, conexión abruptamente cerrada por el jugador')
            break
    
    aux.establecerLongitudPalabra(partida, jugadores, cerrojo)

    aux.notificar_inicio_juego(jugador, ipPuerto, jugadores)
    
    #añado la palabra a la lista del jugador en el diccionario
    palabra = aux.pedirPalabraOLetra(jugador)     
    cerrojo.acquire()
    jugadores[ipPuerto] = jugadores[ipPuerto] + [palabra]    
    cerrojo.release()

    #bucle que no permita continuar hasta que los 2 jugadores tienen la palabra colocada
    while True:
        nJugadoresConPalabraColocada = sum( [len(lista)>=4 for (_,lista) in [list(jugadores.items())[i] for i in pareja]] )
        if nJugadoresConPalabraColocada == 2:
            break
        else:
            try:
                jugador.send("Espera porque tu compi todavía no ha elegido la palabra para ti...")
            except IOError:
                print ('No enviado, conexión abruptamente cerrada por el jugador')
            time.sleep(2)

    #establezco estado de SIGUE PROBANDO para cada jugador de la partida en su lista
    #este estado pasará a ser GANADOR si gana o AGOTADO INTENTOS si se ahorca
    for (ip, lista) in jugadores.items():
            if lista[0] == partida:
                if len(lista) < 5:
                    cerrojo.acquire()
                    jugadores[ip] = jugadores[ip] + ['sigue probando']  
                    cerrojo.release()

    jugador.send('COMIENZA EL JUEGO DEL  A H O R C A D O')
    palabraContr = aux.palabracontraria(partida, jugadores, ipPuerto)
    aux.ahorcado(jugador, ipPuerto, palabraContr, jugadores, partida, cerrojo, pareja, pos)

    if jugadores[ipPuerto][4] == 'ganador':
        try:
            jugador.send("ENHORABUENA")
        except IOError:
                print ('No enviado, conexión abruptamente cerrada por el jugador')
    if jugadores[ipPuerto][4] == 'sigue probando':
        try:
            jugador.send("JUEGO FINALIZADO")
        except IOError:
                print ('No enviado, conexión abruptamente cerrada por el jugador')
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
                break
            elif jugadores[contrincante][4] == 'agotado intentos':
                try:
                    jugador.send("FINALMENTE NINGUNO DE LOS DOS HABEIS GANADO LA PARTIDA")
                except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                break
            else: #mi contrincante sigue con el estado 'sigue probando'
                try:
                    jugador.send("espera a ver qué pasa con tu contrincante...")
                except IOError:
                    print ('No enviado, conexión abruptamente cerrada por el jugador')
                time.sleep(2)

    jugador.close()

    Process(target = aux.publicarResultados, args = ( jugadores[ipPuerto],)).start()

    #antes de ejecutar esto me tengo que asegurar que ambos han terminado porque sino da fallo
    #time.sleep(10) #FULLERÍA

    #cerrojo.acquire()
    #aux.borrarParejaDict(pareja, jugadores, ipPuerto)
    #cerrojo.release()


    
if __name__ == '__main__':

    servidor = Listener(address=('127.0.0.1', 6000), authkey=b'secret password SERVER')
    print ('Iniciando servidor del ahorcado...')
    
    manager = Manager()
    jugadores = manager.dict()
    cerrojo = Lock()

    while True:
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
            
            p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo))
            p.start()

        except AuthenticationError:
            print ('Conexión rechaza, contraseña incorrecta')


    servidor.close()
    print ('FIN')
