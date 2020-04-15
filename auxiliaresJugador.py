# -*- coding: utf-8 -*-
# datos o funciones auxiliares para mantener ordenado nuestro codigo del jugador

import time


def enviarPalabraParaContrincante(longitud):
    """
    Función que, dada la longitud de una palabra, devuelve la palabra pedida al
    usuario que recibe el mensaje.

    Parameters
    ----------
    longitud : int
        Longitud de la palabra.

    Returns
    -------
    palabra: str
        Palabra escrita por el usuario.
    """

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
    """
    Función que, dada una lista de las letras probadas ya, devuelve un intento para 
    introducir una letra nueva pedida al usuario.

    Parameters
    ----------
    letrasProbadas : list
        Lista de letras ya recibidas por el usuario.

    Returns
    -------
    intento : str
        Letra introducida por el usuario.
    
    """

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
