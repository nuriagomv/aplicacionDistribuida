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
            jugador.send('Esperando al segundo jugador...')
            time.sleep(3)
        else:
            jugador.send('Ya sois dos jugadores AÑADIR COMO SE LLAMA EL COMPAÑERO, empieza la partida...')
            break
    pareja = np.where( [lista[0]==partida for (_,lista) in jugadores.items()] )[0]
    
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
            jugador.send("Espera porque tu compi todavía no ha elegido la palabra para ti...")
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
        jugador.send("ENHORABUENA")
    if jugadores[ipPuerto][4] == 'sigue probando':
        jugador.send("JUEGO FINALIZADO")
    if jugadores[ipPuerto][4] == 'agotado intentos': # mi contrincante tiene oportunidad de ganar todavia
        #establezco la ip de mi contrincante:
        for (ip,_) in [list(jugadores.items())[i] for i in pareja]:
            if ip != ipPuerto: #la ip es la de mi contrincante, no la mía
                contrincante = ip
                break
        while True:
            if jugadores[contrincante][4] == 'ganador':
                jugador.send("FINALMENTE TU CONTRINCANTE HA GANADO LA PARTIDA")
                break
            elif jugadores[contrincante][4] == 'agotado intentos':
                jugador.send("FINALMENTE NINGUNO DE LOS DOS HABEIS GANADO LA PARTIDA")
                break
            else: #mi contrincante sigue con el estado 'sigue probando'
                jugador.send("espera a ver qué pasa con tu contrincante...")
                time.sleep(2)

    while True:
        time.sleep(1) #para qe no se cierre ninguna conexión
    #jugador.close()
    #cerrojo.acquire()
    #del jugadores[ipPuerto] # lo borro del diccionario
    # tengo que borrar a ambos a la vez pa q no se quede un proceso colgao
    #cerrojo.release()


    #Y YA AL FINAL DEL TODISIMO SE PUBLICARIAN LOS RESULTADOS EN UN TOPIC DEL BROKER WILD.MAT.UCM.ES
        

    
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
            
            infoApodoJugador = jugador.recv()
            jugadores[ipPuerto] = infoApodoJugador
            
            p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo))
            p.start()

        except AuthenticationError:
            print ('Conexión rechaza, contraseña incorrecta')


    servidor.close()
    print ('FIN')
