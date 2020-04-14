"""
PRESENTACIÓN
"""

from multiprocessing.connection import Listener, AuthenticationError
from multiprocessing import Process, Lock, Manager, Value
import random
import time
import numpy as np
import auxiliaresServidor as aux


def serve_client(jugador, ipPuerto, jugadores, cerrojo, juegoActivo, jugadoresFinalizados):

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

    juegosActivos = []
    contadoresFinalizados = []
    var = -1

    while True:
        var += 1
        print("Configurando una nueva partida...")

        juegosActivos.append( manager.Value("c_bool", True) )
        contadoresFinalizados.append( manager.Value("i",0) )
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
                
                p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo, juegosActivos[var], contadoresFinalizados[var]))
                p.start()

            except AuthenticationError:
                print ('Conexión rechaza, contraseña incorrecta')


    servidor.close()
    print ('FIN')
