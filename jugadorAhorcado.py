from multiprocessing.connection import Client, Listener
from multiprocessing import Process
import time


local_listener = (('127.0.0.1', 5001), b'secret password CLIENT')

def enviarPalabraParaContrincante(longitud):
    l = int(longitud[len(longitud)-1]) #ultimo elemento del mensaje en el que se indica la longitud
    while True:
        print('Adivina una letra.')
        palabra = input('Propón una palabra para tu contrincante de la longitud indicada: ')
        palabra.lower()
        if len(palabra) != l:
            print('Por favor, que sea de la longitud indicada.')
        elif not all([char in "abcdefghijklmnñopqrstuvwxyz" for char in palabra]):
            print('Por favor, ingresa una PALABRA.')
        else:
            return palabra



def jugador_listener():
    jugadorListener = Listener(address = local_listener[0], authkey = local_listener[1])
    
    servidor = jugadorListener.accept()
    
    longitud = servidor.recv()
    print ('Primer mensaje del servidor recibido:', longitud)

    #palabraParaContrincante = enviarPalabraParaContrincante(longitud)

    #servidor.send(palabraParaContrincante)



if __name__ == '__main__':

    print ('intentando conectar con en el servidor para jugar al ahorcado...')
    jugador = Client(address = ('127.0.0.1', 6000), authkey = b'secret password SERVER')
    print ('Conexión aceptada')
    apodo = input('Cuál es tu apodo como jugador? ')
    jugador.send([local_listener, apodo])
    print ('enviando la información de tu listener como jugador...')

    jugadorListener = Process(target=jugador_listener, args=())
    jugadorListener.start()

    try:
        saludo = jugador.recv()
        print (saludo)
    except EOFError:
        print('No recibido, conexión abruptamente cerrada')
        
        
        
    #jugador.close()
    #jugadorListener.terminate()
    #print("JUEGO FINALIZADO")