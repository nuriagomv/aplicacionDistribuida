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



def obtenerIntento(letrasProbadas):
    # Devuelve la letra ingresada por el jugador. Verifica que el jugador ha ingresado sólo una letra, y no otra cosa.
    while True:
        print('Adivina una letra.')
        intento = input()
        intento = intento.lower()
        if len(intento) != 1:
            print('Por favor, introduce una letra.')
        elif intento in letrasProbadas:
            print('Ya has probado esa letra. Elige otra.')
        elif intento not in 'abcdefghijklmnñopqrstuvwxyz':
            print('Por favor ingresa una LETRA.')
        else:
            return intento



print('A H O R C A D O')
letrasIncorrectas = ''
letrasCorrectas = ''
palabraSecreta = ''
juegoTerminado = False

while True:
    mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabraSecreta)

    # Permite al jugador escribir una letra.
    intento = obtenerIntento(letrasIncorrectas + letrasCorrectas)

    if intento in palabraSecreta:
        letrasCorrectas = letrasCorrectas + intento

    # Verifica si el jugador ha ganado.
    encontradoTodasLasLetras = True
    for i in range(len(palabraSecreta)):
        if palabraSecreta[i] not in letrasCorrectas:
            encontradoTodasLasLetras = False
            break
    if encontradoTodasLasLetras:
        print('¡Sí! ¡La palabra secreta es "' + palabraSecreta + '"! ¡Has ganado!')
        juegoTerminado = True
    else:
        letrasIncorrectas = letrasIncorrectas + intento

    # Comprobar si el jugador ha agotado sus intentos y ha perdido.
    if len(letrasIncorrectas) == len(listaMonigotes) - 1:
        mostrarTablero(listaMonigotes, letrasIncorrectas, letrasCorrectas, palabraSecreta)
        print('¡Te has quedado sin intentos!\nDespués de ' + str(len(letrasIncorrectas)) + ' intentos fallidos y ' + str(len(letrasCorrectas)) + ' aciertos, la palabra era "' + palabraSecreta + '"')
        juegoTerminado = True


    if juegoTerminado:
        print("FINAL DEL JUEGO")