from multiprocessing.connection import Client

print ('intentando acceder al servidor para jugar al ahorcado...')
jugador = Client(address=('127.0.0.1', 6000), authkey=b'secret password')
print ('Conexión aceptada')

message = input('Apodo como jugador? ')
jugador.send(message)
print ('enviando tu apodo...')
answer = jugador.recv() 
print ('respuesta:', answer) 

jugador.close()
