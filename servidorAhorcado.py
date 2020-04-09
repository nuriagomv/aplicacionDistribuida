from multiprocessing.connection import Listener, Client, AuthenticationError
from multiprocessing import Process, Lock, Manager
import random
import time



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


def mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabraSecreta):
    espaciosVacios = '_' * len(palabraSecreta)
    for i in range(len(palabraSecreta)): # completar los espacios vacíos con las letras adivinadas
        if palabraSecreta[i] in letrasCorrectas:
            espaciosVacios = espaciosVacios[:i] + palabraSecreta[i] + espaciosVacios[i+1:]
    envio = listaMonigotes[len(letrasIncorrectas)]+'\n'*2+'Letras incorrectas: '+str(letrasIncorrectas)+'\n'+'Lo que llevas de la palabra: '+str(espaciosVacios)+'\n'
    return envio


def pedirPalabraOLetra(conn): 
    try:
        m = conn.recv()
    except EOFError:
        print('algo no ha funcionado')
    return m


def localizarJugador(pareja, ipPuerto):
    i = -1
    for (_, items) in pareja.items():
        i += 1
        if items == pareja[ipPuerto]:
            break
    return i


def colocarPalabra(pareja, palabra, ipPuerto):
    pareja['palabras'] = [(1, 'palabra'), (2, 'palabra')]

    i = localizarJugador(pareja, ipPuerto)

    pareja['palabras'][i] = (i+1, palabra)
    print('El jugador ', i+1, ' propone la palabra: ', palabra)


def notificar_inicio_juego(pareja):
    print('INICIO JUEGO')
    lonPalabra = random.randint(4,8)
    for (jugador, [jugador_info, _]) in pareja.items():
        print ("Mandando longitud de palabra a ", jugador)
        conn = Client(address=jugador_info[0], authkey=jugador_info[1])
        conn.send("Elige una palabra de longitud "+str(lonPalabra))

        # Process(target=pedirPalabraOLetra, args=(conn,)).start()
        conn.close()


#def saludar(ipPuerto, jugadores):
#    j = len(jugadores)
#    [jugador_info, apodo] = jugadores[ipPuerto]
#    jugador = Client(address= jugador_info[0], authkey=jugador_info[1])
#    if j == 1:
#        jugador.send('Hola '+apodo+' tu papel es de Jugador 1. \n Esperando al segundo jugador...')
#    if j == 2:
#        jugador.send('Hola '+apodo+' tu papel es de Jugador 2. \n Ya tenemos dos jugadores, empieza la partida...')
#    jugador.close()


def palabracontraria(palabra, diccionario):
  for (_,p) in diccionario['palabras']:
    if p != palabra:
      return p


def ahorcado(jugador, ipPuerto, palabra, pareja):
    #ahora aqui ya debe empezar el bucle del ahorcado
    #el bucle (juego) terminará cuando el nIntentos==nTotalIntentos o cuando el otro jugador gane
    #LISTA MONIGOTES Y NTOTALINTENTOS DEBERIA METERLOS DENTRO DE SERVER_CLIENT
    jugador_info, _ = pareja[ipPuerto]
    conn = Client(address=jugador_info[0], authkey=jugador_info[1])
    conn.send('COMIENZA EL JUEGO DEL A H O R C A D O')
    juegoContinua = True
    letrasCorrectas = []
    letrasIncorrectas = []
    nIntentosFallidos = 0
    
    while juegoContinua:
        juegoContinua = not ( nIntentosFallidos==nTotalIntentos or
         any([x=='ganador' for (_,x) in pareja['haGanado']]) )
        
        letra = pedirPalabraOLetra(jugador)
        if letra in palabra:
            letrasCorrectas.append(letra)
        else:
            letrasIncorrectas.append(letra)
        
        if all([char in letrasCorrectas for char in palabra]):
            i = localizarJugador(pareja, ipPuerto)
            pareja['haGanado'][i] = (i+1, 'ganador')
            print('EL JUGADOR ', i+1, ' HA GANADO!!!')
            jugador.send("HAS GANADO, LA PALABRA ERA "+palabra)
            jugador.close()
            break

        jugador.send( '\n'+mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabra) )
        nIntentosFallidos = len(letrasIncorrectas)



def serve_client(jugador, ipPuerto, jugadores, cerrojo):

    #formar la pareja
    while True:
        if len(jugadores) == 2:
            cerrojo.acquire()
            pareja = jugadores.copy()
            jugadores.clear()
            cerrojo.release()
            break
    
    notificar_inicio_juego(pareja)
    
    # A PARTIR DE AQUI FALLA PARA EL SEGUNDO JUGADOR QUE ABRO
    palabra = pedirPalabraOLetra(jugador)

    colocarPalabra(pareja, palabra, ipPuerto)
    pareja['haGanado'] = [(1,'no'), (2,'no')]

    print(pareja) #borrar cuando ya compruebe que el diccionario está bien


    ahorcado(jugador, ipPuerto, palabracontraria(palabra,pareja), pareja)

    jugador.close() #DEBERÉ CERRAR A AMBOS JUGADORES
    

    #ADEMAS ME QUEDA EL CASO DE COMPROBAR SI TERMINA CUANDO AGOTA INTENTOS
    # SI TERMINARIA PARA AMBOS O SOLO PARA UNO Y ESPERA O QUE PASA
    #Y YA AL FINAL DEL TODISIMO SE PUBLICARIAN LOS RESULTADOS
        
    




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
            
            #saluda antes de pasar la conexión a un proceso
            j = len(jugadores)
            if j == 1:
                jugador.send('Hola '+infoListenerApodoJugador[1]+' tu papel es de Jugador 1. \n Esperando al segundo jugador...')
            if j == 2:
                jugador.send('Hola '+infoListenerApodoJugador[1]+' tu papel es de Jugador 2. \n Ya tenemos dos jugadores, empieza la partida...')

            p = Process(target=serve_client, args=(jugador, ipPuerto, jugadores, cerrojo))
            p.start()

        except AuthenticationError:
            print ('Conexión rechaza, contraseña incorrecta')


    servidor.close()
    print ('FIN')
