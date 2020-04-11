from multiprocessing.connection import Listener, AuthenticationError #, Client
from multiprocessing import Process, Lock, Manager
import random
import time
import numpy as np



listaMonigotes = ['''
    ''', '''
 
   +---+
   |   |
       |
       |
       |
       |
 =========''', '''
 
   +---+
   |   |
   O   |
       |
       |
       |
 =========''', '''
 
   +---+
   |   |
   O   |
   |   |
       |
       |
 =========''', '''
 
   +---+
   |   |
   O   |
  /|   |
       |
       |
 =========''', '''
 
   +---+
   |   |
   O   |
  /|\  |
       |
       |
 =========''', '''
 
   +---+
   |   |
   O   |
  /|\  |
  /    |
       |
 =========''', '''
 
   +---+
   |   |
   O   |
  /|\  |
  / \  |
       |
 =========''']

nTotalIntentos = len(listaMonigotes) - 1


def decidirPartidaParaJugador(jugadores, ipPuerto):
    claves = np.array( list(jugadores.keys()) )
    pos = list ( np.where(claves == ipPuerto)[0] )[0] + 1
    if pos % 2 == 0: # la posición es par
        partida = pos/2
    else: # la posición es impar
        partida = (pos-1)/2 + 1
    return int(pos), int(partida)

def saludar(apodo, pos, jugador):
    if pos % 2 != 0:
        jugador.send('Hola '+apodo+' tu papel es de Jugador 1.')
    else:
        jugador.send('Hola '+apodo+' tu papel es de Jugador 2.')

def establecerLongitudPalabra(partida, jugadores, cerrojo):
    lonPalabra = random.randint(4,6)
    for (ip, lista) in jugadores.items():
            if lista[0] == partida:
                if len(lista) < 3:
                    cerrojo.acquire()
                    jugadores[ip] = jugadores[ip] + [lonPalabra]
                    cerrojo.release()

def notificar_inicio_juego(jugador, ipPuerto, jugadores):
    lonPalabra = jugadores[ipPuerto][2]
    print ("Mandando longitud de palabra a ", jugadores[ipPuerto][1], ' que está en ', ipPuerto)
    jugador.send("Elige una palabra de longitud "+str(lonPalabra))

def pedirPalabraOLetra(jugador): 
    try:
        m = jugador.recv()
    except EOFError:
        print('algo no ha funcionado')
    return m

def palabracontraria(partida, jugadores, ipPuerto):
    for (ip, lista) in jugadores.items():
            if lista[0] == partida:
                if ip != ipPuerto:
                    palabraContr = lista[3]
                    break
    return palabraContr

def mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabraSecreta):
    espaciosVacios = '_' * len(palabraSecreta)
    for i in range(len(palabraSecreta)): # completar los espacios vacíos con las letras adivinadas
        if palabraSecreta[i] in letrasCorrectas:
            espaciosVacios = espaciosVacios[:i] + palabraSecreta[i] + espaciosVacios[i+1:]
    envio = listaMonigotes[len(letrasIncorrectas)]+'\n'*2+'Letras incorrectas: '+str(letrasIncorrectas)+'\n'+'Lo que llevas de la palabra: '+str(espaciosVacios)+'\n'
    return envio

def ahorcado(jugador, ipPuerto, palabra, jugadores, partida, cerrojo, pareja):
    
    #LISTA MONIGOTES Y NTOTALINTENTOS DEBERIA METERLOS DENTRO

    juegoContinua = True
    letrasCorrectas = []
    letrasIncorrectas = []
    nIntentosFallidos = 0

    while juegoContinua:
        #el bucle (juego) terminará cuando el nIntentos==nTotalIntentos o cuando algun jugador gane
        juegoContinua = not ( nIntentosFallidos==nTotalIntentos or
                            any([ lista[4]=='ganador' for (_,lista) in [list(jugadores.items())[i] for i in pareja] ]) )
        
        letra = pedirPalabraOLetra(jugador)
        if letra in palabra:
            letrasCorrectas.append(letra)
        else:
            letrasIncorrectas.append(letra)
        
        #si ha acertado todas las letras es ganador
        if all([char in letrasCorrectas for char in palabra]):
            cerrojo.acquire()
            jugadores[ipPuerto] = jugadores[ipPuerto][0:4]+['ganador']  #NO ME ACTUALIZA ESTO!!!!!!!!
            cerrojo.release()
            jugador.send("HAS GANADO, la palabra era "+palabra)
            print(jugadores) #sobra
            break
        
        #si ha agotado todos sus intentos
        nIntentosFallidos = len(letrasIncorrectas)
        if nIntentosFallidos == nTotalIntentos:
            cerrojo.acquire()
            jugadores[ipPuerto] = jugadores[ipPuerto][0:4]+['agotado intentos'] #NO ME ACTUALIZA ESTO!!!!!!!!
            cerrojo.release()
            jugador.send("HAS AGOTADO TODOS TUS INTENTOS, la palabra era "+palabra)
            print(jugadores) #sobra
            break

        jugador.send( '\n'+mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabra) )
        

def serve_client(jugador, ipPuerto, jugadores, cerrojo):

    #asigno una partida al jugador:
    pos, partida = decidirPartidaParaJugador(jugadores, ipPuerto)
    apodo = jugadores[ipPuerto][0]
    
    cerrojo.acquire()
    jugadores[ipPuerto] = [partida] + jugadores[ipPuerto]
    cerrojo.release()
    
    saludar(apodo, pos, jugador)

    #espero a que haya dos jugadores asignados a la misma partida para empezar
    while True:
        if sum( [lista[0]==partida for (_,lista) in jugadores.items()] ) != 2:
            jugador.send('Esperando al segundo jugador...')
            time.sleep(3)
        else:
            jugador.send('Ya sois dos jugadores AÑADIR COMO SE LLAMA EL COMPAÑERO, empieza la partida...')
            break
    pareja = np.where( [lista[0]==partida for (_,lista) in jugadores.items()] )[0]
    
    establecerLongitudPalabra(partida, jugadores, cerrojo)

    notificar_inicio_juego(jugador, ipPuerto, jugadores)
    
    #añado la palabra a la lista del jugador en el diccionario
    palabra = pedirPalabraOLetra(jugador)
    cerrojo.acquire()
    jugadores[ipPuerto] = jugadores[ipPuerto] + [palabra]
    cerrojo.release()

    #bucle que no permita continuar hasta que los 2 jugadores tienen la palabra colocada
    while True:
        nJugadoresConPalabraColocada = sum( [len(lista)>=4 for (_,lista) in [list(jugadores.items())[i] for i in pareja]] )
        if nJugadoresConPalabraColocada == 2:
            break
        else:
            jugador.send("Espera porque tu compi todavía no ha elegido la palabra para ti...")
            time.sleep(2)

    #establezco estado de SIGUE PROBANDO para cada jugador de la partida en su lista
    #este estado pasará a ser GANADOR si gana o AGOTADO INTENTOS si se ahorca
    for (ip, lista) in jugadores.items():
            if lista[0] == partida:
                if len(lista) < 5:
                    cerrojo.acquire()
                    jugadores[ip] = jugadores[ip] + ['sigue probando']
                    cerrojo.release()

    jugador.send('COMIENZA EL JUEGO DEL  A H O R C A D O')
    ahorcado(jugador, ipPuerto, palabracontraria(partida, jugadores, ipPuerto), jugadores, partida, cerrojo, pareja)

    if jugadores[ipPuerto][4] == 'ganador':
        jugador.send("ENHORABUENA")
    if jugadores[ipPuerto][4] == 'sigue probando':
        jugador.send("JUEGO FINALIZADO: TU CONTRINCANTE HA GANADO")
    if jugadores[ipPuerto][4] == 'agotado intentos': # mi contrincante tiene oportunidad de ganar todavia
        for (ip,_) in [list(jugadores.items())[i] for i in pareja]:
            if ip != ipPuerto:
                contrincante = ip
                break
        while True:
            if jugadores[contrincante] == 'ganador':
                jugador.send("FINALMENTE TU CONTRINCANTE HA GANADO LA PARTIDA")
                break
            elif jugadores[contrincante] == 'agotado intentos':
                jugador.send("FINALMENTE NINGUNO DE LOS DOS HABEIS GANADO LA PARTIDA")
                break
            else:
                jugador.send("espera a ver qué pasa con tu contrincante...")
                time.sleep(2)

    jugador.close()
    cerrojo.acquire()
    #del jugadores[ipPuerto] # lo borro del diccionario
    # tengo que borrar a ambos a la vez pa q no se quede un proceso colgao
    cerrojo.release()


    #Y YA AL FINAL DEL TODISIMO SE PUBLICARIAN LOS RESULTADOS EN UN TOPIC DEL BROKER WILD.MAT.UCM.ES
        
    
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
            
            p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo))
            p.start()

        except AuthenticationError:
            print ('Conexión rechaza, contraseña incorrecta')


    servidor.close()
    print ('FIN')
