from multiprocessing.connection import Listener, Client, AuthenticationError
from multiprocessing import Process, Lock, Manager
import random
import time



def pedirPalabras(conn):
    try:
        palabra = conn.recv()
        print(palabra)
    except EOFError:
        print('algo no ha funcionado')
    #return palabra


def notificar_inicio_juego(pareja):
    print('INICIO JUEGO')
    lonPalabra = random.randint(4,8)
    for (jugador, [jugador_info, _]) in pareja.items():
        print ("Mandando longitud de palabra a ", jugador)
        conn = Client(address=jugador_info[0], authkey=jugador_info[1])
        conn.send("Elige una palabra de longitud "+str(lonPalabra))

        # Process(target=pedirPalabras, args=(conn,)).start()
        conn.close()


def saludar(ipPuerto, jugadores):
    j = len(jugadores)
    [jugador_info, apodo] = jugadores[ipPuerto]
    jugador = Client(address= jugador_info[0], authkey=jugador_info[1])
    if j == 1:
        jugador.send('Hola '+apodo+' tu papel es de Jugador 1. \n Esperando al segundo jugador...')
    if j == 2:
        jugador.send('Hola '+apodo+' tu papel es de Jugador 2. \n Ya tenemos dos jugadores, empieza la partida...')
    jugador.close()
    time.sleep(2)  #por no empezar tan pronto el juego




def serve_client(jugador, ipPuerto, jugadores, cerrojo):

    #formar la pareja
    while True:
        if len(jugadores) == 2:
            cerrojo.acquire()
            pareja = jugadores.copy()
            jugadores.clear()
            cerrojo.release()
            break
    
    notificar_inicio_juego(pareja)



    juegoContinua = True
    while juegoContinua:
        try:
            m = jugador.recv()
        except EOFError:
            print ('conexión abruptamente cerrada por el jugador')
            juegoContinua = False
        print ('Mensaje recibido: ', m, ' de ', ipPuerto)
        if m == "quit":    
            juegoContinua = False
            jugador.close() 
    #del jugadores[ipPuerto]                       
    #notify_quit_client(id, clients)            
    print (ipPuerto, 'ha cerrado conexión')
        
    




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
            
            infoListenerApodoJugador = jugador.recv()
            jugadores[ipPuerto] = infoListenerApodoJugador
            
            #saluda antes de pasar la conexión a un proceso
            j = len(jugadores)
            if j == 1:
                jugador.send('Hola '+infoListenerApodoJugador[1]+' tu papel es de Jugador 1. \n Esperando al segundo jugador...')
            if j == 2:
                jugador.send('Hola '+infoListenerApodoJugador[1]+' tu papel es de Jugador 2. \n Ya tenemos dos jugadores, empieza la partida...')

            p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo))
            p.start()

        except AuthenticationError:
            print ('Conexión rechaza, contraseña incorrecta')

    servidor.close()
    print ('FIN')
