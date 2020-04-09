from multiprocessing.connection import Client, Listener
from multiprocessing import Process, Manager
import time


local_listener = (('127.0.0.1', 5002), b'secret password CLIENT')

def enviarPalabraParaContrincante(longitud):
    while True:
        palabra = input('Propón una palabra para tu contrincante de la longitud indicada: ')
        palabra.lower()
        if len(palabra) != longitud:
            print('Por favor, que sea de la longitud indicada.')
        elif not all([char in "abcdefghijklmnñopqrstuvwxyz" for char in palabra]):
            print('Por favor, ingresa una PALABRA.')
        else:
            return palabra


def jugador_listener(avisos):
    jugadorListener = Listener(address = local_listener[0], authkey = local_listener[1])
    
    while True:
        servidor = jugadorListener.accept()
        mensaje = servidor.recv()
        print ('Mensaje del servidor recibido:', mensaje)

        if "Elige una palabra" in mensaje:
            avisos['longitudDada'] = ["sí", int(mensaje[len(mensaje)-1])]








if __name__ == '__main__':

    print ('intentando conectar con en el servidor para jugar al ahorcado...')
    jugador = Client(address = ('127.0.0.1', 6000), authkey = b'secret password SERVER')
    print ('Conexión aceptada')
    apodo = input('Cuál es tu apodo como jugador? ')
    jugador.send([local_listener, apodo])
    print ('enviando la información de tu listener como jugador...')

    saludo = jugador.recv()
    print(saludo)

    manager = Manager()
    avisos = manager.dict()
    avisos['longitudDada'] = ["no"]
    avisos['juegoFinalizado'] = "no"

    jugadorListener = Process(target=jugador_listener, args=(avisos,))
    jugadorListener.start()

    while not (avisos['juegoFinalizado'] == "sí") :

        if (avisos['longitudDada'][0] == "sí"):
            palabraElegida = enviarPalabraParaContrincante(avisos['longitudDada'][1])
            jugador.send(palabraElegida)



        
    #jugador.close()
    #jugadorListener.terminate()
    #print("JUEGO FINALIZADO")