from multiprocessing.connection import Client
import time


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
            longitud =  int( mensaje[len(mensaje)-1] ) #el último elemento del mensaje
            palabraElegida = enviarPalabraParaContrincante(longitud)
            jugador.send(palabraElegida)
        if "COMIENZA EL JUEGO" in mensaje:
            break #me salgo de este primer bucle cuando puedo comenzar el juego

    #bucle para jugar al ahorcado
    letrasProbadas = []
    continuar = True
    while continuar:
        try:
            intento =  obtenerIntento(letrasProbadas)
            jugador.send(intento)
            letrasProbadas.append(intento)
            respuesta = jugador.recv()
            print(respuesta)
        except:
            print('parece que ha habido algun error')
        if ("HAS GANADO" in respuesta) or ("HAS AGOTADO" in respuesta) or ("TU CONTRINCANTE" in respuesta): #en caso contrario, es que me ha mandado el monigote y no un mensaje
            continuar = False
    
    #respuesta final por parte del servidor
    while True:
        try:
            fin = jugador.recv()
            print(fin)
        except:
            print("parece que algo está fallando")
        if ("ENHORABUENA" in fin) or ("JUEGO FINALIZADO" in fin) or ("FINALMENTE" in fin): #en caso contrario, es que mi contrincante sigue jugando
            break

    #jugador.close()
    print("FIN")