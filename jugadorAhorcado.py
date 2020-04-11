from multiprocessing.connection import Client #, Listener
from multiprocessing import Process, Manager
import time


#local_listener = (('127.0.0.1', 5001), b'secret password CLIENT')


def enviarPalabraParaContrincante(longitud):
    time.sleep(1)
    while True:
        palabra = input('Propón una palabra para tu contrincante de la longitud indicada: ')
        palabra.lower()
        if len(palabra) != longitud:
            print('Por favor, que sea de la longitud indicada.')
        elif not all([char in "abcdefghijklmnñopqrstuvwxyz" for char in palabra]):
            print('Por favor, ingresa una PALABRA.')
        else:
            return palabra

def obtenerIntento(letrasProbadas):
    while True:
        time.sleep(1) 
        intento = input('Adivina una de las letras: ')
        intento = intento.lower()
        if len(intento) != 1:
            print('Por favor, introduce UNA letra.')
        elif intento in letrasProbadas:
            print('Ya has probado esa letra. Elige otra.')
        elif intento not in 'abcdefghijklmnñopqrstuvwxyz':
            print('Por favor ingresa una LETRA.')
        else:
            return intento


#def jugador_listener(avisos):
#    jugadorListener = Listener(address = local_listener[0], authkey = local_listener[1])
#    while True:
#        servidor = jugadorListener.accept()
#        mensaje = servidor.recv()
#        print ('Mensaje del servidor recibido: ', mensaje)
#
#        if "Elige una palabra" in mensaje:
#            avisos['longitudDada'] = ["sí", int(mensaje[len(mensaje)-1])]
#            print(avisos['longitudDada'])



if __name__ == '__main__':

    print ('intentando conectar con en el servidor para jugar al ahorcado...')
    jugador = Client(address = ('127.0.0.1', 6000), authkey = b'secret password SERVER')
    print ('Conexión aceptada')
    apodo = input('Cuál es tu apodo como jugador? ')
    jugador.send([apodo])
    print ('enviando la información de tu listener como jugador...')

    while True:
        mensaje = jugador.recv()
        print('MANDADO DESDE SERVIDOR: ', mensaje)
        if "Elige una palabra" in mensaje:
            longitud =  int(mensaje[len(mensaje)-1])
            palabraElegida = enviarPalabraParaContrincante(longitud)
            jugador.send(palabraElegida)
            
    
   

    #manager = Manager()
    #avisos = manager.dict()
    #avisos['longitudDada'] = ["no"]
    #avisos['juegoFinalizado'] = "no"
    #avisos['escucharOcontestar'] = "escuchar"

    #jugadorListener = Process(target=jugador_listener, args=(avisos,))
    #jugadorListener.start()

    #while True:
    #    if (avisos['longitudDada'][0] == "sí"):
    #        palabraElegida = enviarPalabraParaContrincante( avisos['longitudDada'][1] )
    #        jugador.send(palabraElegida)
    #        break
    
    #letrasProbadas = []
    #while not (avisos['juegoFinalizado'] == "sí") :
    #    intento =  obtenerIntento(letrasProbadas)
    #    jugador.send(intento)
    #    letrasProbadas.append(intento)
    #    respuesta = jugador.recv()
    #    print(respuesta)
    #    if "HAS GANADO" in respuesta:
    #        avisos['juegoFinalizado'] = "sí"


    #jugador.close()
    #jugadorListener.terminate()
    #print("JUEGO FINALIZADO")