from multiprocessing.connection import Listener
from multiprocessing import Process
from multiprocessing.connection import AuthenticationError
from time import time



def ahorcado(jugador1, jugador2):
    apodos = []
    for jugador in [jugador1,jugador2]:
        try:
            m = jugador.recv()
        except EOFError:
            print ('No receive, connection abruptly closed by client')
            break
        apodos.append(m)

    answer = 'hola jugadores '+apodos[0]+" y "+apodos[1]
    
    for jugador in [jugador1,jugador2]:
        try:
            jugador.send(answer)
        except IOError:
            print ('No send, connection abruptly closed by client')
            break

    for jugador in [jugador1,jugador2]:
        jugador.close()
        print ('connection closed')




if __name__ == '__main__':
    servidor = Listener(address=('127.0.0.1', 6000), authkey=b'secret password')
    print ('El servidor del juego del ahorcado se ha iniciado')

    while True:
        print ('\nEsperando jugadores...')
        try:
            jugador = servidor.accept()  #acepto conexión              
            print ('Conexión aceptada para Jugador 1 desde', servidor.last_accepted)
            jugador1 = jugador
            print('Tenemos al jugador 1. Esperando al segundo jugador...')
            jugador2 = servidor.accept()
            print ('Conexión aceptada para Jugador 2 desde', servidor.last_accepted)
            juego = Process(target=ahorcado, args=(jugador1,jugador)) #y se las paso a un proceso
            juego.start()
        except AuthenticationError:
            print ('Conexión rechazada, contraseña incorrecta')
        
    servidor.close()
    print ('end')
