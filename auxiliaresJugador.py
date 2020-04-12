#datos o funciones auxiliares para mantener ordenado nuestro codigo del jugador

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