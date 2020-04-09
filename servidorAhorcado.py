from multiprocessing.connection import Listener, Client, AuthenticationError
from multiprocessing import Process, Lock, Manager
import random
import time



listaMonigotes = ['''
 
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

nTotalIntentos = len(listaMonigotes)

def mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabraSecreta):
    print(listaMonigotes[len(letrasIncorrectas)-1])
    print()
 
    print('Letras incorrectas: ', letrasIncorrectas,'\n')

    espaciosVacios = '_' * len(palabraSecreta)
    for i in range(len(palabraSecreta)): # completar los espacios vacíos con las letras adivinadas
        if palabraSecreta[i] in letrasCorrectas:
            espaciosVacios = espaciosVacios[:i] + palabraSecreta[i] + espaciosVacios[i+1:]

    print('Lo que llevas de la palabra: ',espaciosVacios, '\n')


def pedirPalabras(conn): #también se puede aprovechar para pedir letras
    try:
        palabra = conn.recv()
    except EOFError:
        print('algo no ha funcionado')
    return palabra


def colocarPalabra(pareja, palabra, ipPuerto):
    pareja['palabras'] = [(1, 'palabra1'), (2, 'palabra2')]
    i = -1
    for (_, items) in pareja.items():
        i += 1
        if items == pareja[ipPuerto]:
            break
    pareja['palabras'][i] = (i+1, palabra)
    print('El jugador ', i+1, ' propone la palabra: ', palabra)


def notificar_inicio_juego(pareja):
    print('INICIO JUEGO')
    lonPalabra = random.randint(4,8)
    for (jugador, [jugador_info, _]) in pareja.items():
        print ("Mandando longitud de palabra a ", jugador)
        conn = Client(address=jugador_info[0], authkey=jugador_info[1])
        conn.send("Elige una palabra de longitud "+str(lonPalabra))

        # Process(target=pedirPalabras, args=(conn,)).start()
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




def serve_client(jugador, ipPuerto, jugadores, cerrojo):

    #formar la pareja
    while True:
        if len(jugadores) == 2:
            cerrojo.acquire()
            pareja = jugadores.copy()
            pareja['haGanado'] = [(1,'no'), (2,'no')]
            jugadores.clear()
            cerrojo.release()
            break
    
    notificar_inicio_juego(pareja)
 
    palabra = pedirPalabras(jugador)

    colocarPalabra(pareja, palabra, ipPuerto)

    print(pareja) #borrar cuando ya compruebe que el diccionario está bien


    #ahora aqui ya debe empezar el bucle del ahorcado
    #el bucle (juego) terminará cuando el nIntentos==nTotalIntentos o cuando el otro jugador gane
    #LISTA MONIGOTES Y NTOTALINTENTOS DEBERIA METERLOS DENTRO DE SERVER_CLIENT
    juegoContinua = True
    letrasCorrectas = []
    letrasIncorrectas = []
    nIntentos = 0
    while juegoContinua:
        juegoContinua = not ( nIntentos==nTotalIntentos or any([x=='ganador' for (_,x) in pareja['haGanado']]) )

        #ACTUALIZAR LETRASCORRECTAS LETRASINCORRECTAS SEGUN JUGADOR Y PALABRACONTRARIA (CREO QUE HAY FUNCION)
        #AÑADIR AQUI MOSTRAR TABLERO PARA JUGADOR Y PALABRA CONTRARIA
        try:
            m = jugador.recv()
        except EOFError:
            print ('conexión abruptamente cerrada por el jugador')
            juegoContinua = False
        print ('Mensaje recibido: ', m, ' de ', ipPuerto) 


        if m == "me rindo":    
            juegoContinua = False
            jugador.close() 
    #del jugadores[ipPuerto]                       
    #notify_quit_client(id, clients)            
    print (ipPuerto, 'ha cerrado conexión')
        
    




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
