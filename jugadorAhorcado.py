from multiprocessing.connection import Client, Listener
from multiprocessing import Process
import time

local_listener = (('127.0.0.1', 5003), b'secret password CLIENT')

def jugador_listener():
    jugadorListener = Listener(address = local_listener[0], authkey = local_listener[1])
    print ('Listener del jugador iniciandose...') 
    print ('Aceptando conexiones...')
    while True:
        servidor = jugadorListener.accept()
        print ('Conexión aceptada desde', jugadorListener.last_accepted)       
        m = servidor.recv()
        print ('Mensaje del servidor recibido:', m)



if __name__ == '__main__':

    print ('intentando conectar con en el servidor para jugar al ahorcado...')
    jugador = Client(address = ('127.0.0.1', 6000), authkey = b'secret password SERVER')
    print ('Conexión aceptada')
    jugador.send(local_listener)
    print ('enviando tu información como jugador...')

    jugadorListener = Process(target=jugador_listener, args=())
    jugadorListener.start()

    conectado = True
    while conectado:
        time.sleep(1) #pa que no se me cierre el juego mientras veo lo que tengo q definir aqui

    jugador.close()
    jugadorListener.terminate()
    print("JUEGO FINALIZADO")

