from multiprocessing.connection import Listener, Client, AuthenticationError
from multiprocessing import Process, Lock, Manager
import random
import time


def clear_jugador(clientes, ipPuerto):
    clientes.pop(ipPuerto[1])

def palabraContrincante(board, ipPuerto, m):
    board[ipPuerto[1]] = (m, board[ipPuerto[1]][1]+.05,'#1200FF')
    return board.items()


#def ahorcado(jugador, turno, ipPuerto, palabraAdivinar):
 #   if turno == 1:

  #  if turno == 2:


def notificar_inicio_juego(pareja):
    print('INICIO JUEGO')
    lonPalabra = random.randint(4,8)
    for jugador, jugador_info in pareja.items():
        print ("Mandando longitud de palabra a ", jugador)
        conn = Client(address=jugador_info[0], authkey=jugador_info[1])
        conn.send("Elige una palabra de longitud "+str(lonPalabra))
        conn.close()


def serve_client(jugador, ipPuerto, jugadores, cerrojo):
    j = len(jugadores)
    if j == 1:
        jugador.send('Hola Jugador 1. \n Esperando al segundo jugador...')

    if j == 2:
        jugador.send('Hola Jugador 2. \n Ya tenemos dos jugadores, empieza la partida.')

        cerrojo.acquire()
        pareja = jugadores.copy()
        Process(target=notificar_inicio_juego, args=(pareja,)).start()
        jugadores.clear()
        cerrojo.release()
    
    #jugador.close()
    #print ('Conexion', ipPuerto, 'cerrada')




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
            
            infoListenerJugador = jugador.recv()
            jugadores[ipPuerto] = infoListenerJugador
            
            p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo))
            p.start()
        except AuthenticationError:
            print ('Conexión rechaza, contraseña incorrecta')

    servidor.close()
    print ('FIN')
