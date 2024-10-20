import cv2
import numpy as np
import lib.HandTrackingModule as htm
import time
import pyautogui
import math

# Desativa o sistema de fail-safe do pyautogui
pyautogui.FAILSAFE = False 

"""
O fail-safe é uma medida de segurança que faz com que, se o mouse for movido
para os cantos da tela, o programa é interrompido. Neste caso, está desativado.

https://pyautogui.readthedocs.io/en/latest/#:~:text=As%20a%20safety,the%20fail%20safe.
"""

# Remove a pausa padrão de 0.1 segundo entre comandos do pyautogui.
pyautogui.PAUSE = 0 

"""
A pausa padrão entre os comandos do pyautogui é 0.1 segundo, mas foi configurada
para 0, para remover o atraso entre os comandos.

https://pyautogui.readthedocs.io/en/latest/#:~:text=The%20tenth%2Dsecond%20delay%20is%20set%20by%20the%20pyautogui.PAUSE%20setting%2C%20which%20is%200.1%20by%20default.%20You%20can%20change%20this%20value.
"""

##########################
wCam, hCam = 640, 480 # Largura e altura da câmera
frameR = 100     # definir uma margem na camera, um retângulo dentro da imagem capturada pela câmera, e o movimento do mouse só será registrado dentro dessa área
smoothening = 3  # Suavização do movimento do mouse
##########################

# Inicializando variáveis de tempo e localização
pTime = 0  # Tempo anterior para calcular FPS
plocX, plocY = 0, 0  # Posição anterior do mouse
clocX, clocY = 0, 0  # Posição atual do mouse

# Captura de vídeo pela câmera
cap = cv2.VideoCapture(0)
cap.set(3, wCam)  # Configurando largura da captura de vídeo
cap.set(4, hCam)  # Configurando altura da captura de vídeo

# Inicializando o detector de mãos
detector = htm.handDetector(maxHands=2)  # Detecta até 2 mãos
wScr, hScr = pyautogui.size()  # Obtém as dimensões da tela

# Variáveis de estado para o clique do mouse e zoom
mouse_is_down = False  # Indica se o botão do mouse está pressionado
past_zoom_dist = None  # Guarda a distância anterior entre as mãos para controlar o zoom

while True:
    # Etapa 1: Capturar e detectar mãos
    success, img = cap.read()  # Lê a imagem da câmera
    img, numHands = detector.findHands(img)  # Detecta as mãos
    if numHands == 2:
        lmList2, _ = detector.findPosition(img, 1)  # Captura a posição da segunda mão
    lmList, _ = detector.findPosition(img)  # Captura a posição da primeira mão

    # Etapa 2: Obter as pontas dos dedos indicador e médio
    if numHands != 0:
        x1, y1 = lmList[12][1:]  # Coordenadas da ponta do dedo médio da primeira mão
        if numHands == 2:
            x2, y2 = lmList2[12][1:]  # Coordenadas da ponta do dedo médio da segunda mão

        # Etapa 3: Verificar quais dedos estão levantados
        fingers = detector.fingersUp(lmList)  # Dedos levantados da primeira mão
        if numHands == 2:
            fingers2 = detector.fingersUp(lmList2)  # Dedos levantados da segunda mão

        # Desenha um retângulo ao redor do quadro
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)

        # Etapa 8: Verificar se os dedos indicador e médio estão levantados
        if fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            # Etapa 9: Calcular a distância entre os dedos polegar e indicador
            length, img, lineInfo = detector.findDistance(lmList, 8, 4, img)
            if numHands == 2:
                length2, img2, lineInfo2 = detector.findDistance(lmList2, 8, 4, img)

            # Etapa 10: Se a distância for curta, realizar clique do mouse
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)  # Marca visual do clique
                if numHands == 2:
                    if length2 < 40:
                        # Se as duas mãos estiverem detectadas, calcula a distância entre elas para simular zoom
                        cv2.line(img, (lineInfo[4], lineInfo[5]), (lineInfo2[4], lineInfo2[5]), (255, 0, 255), 3)
                        zoom_dist = math.hypot(lineInfo2[4] - lineInfo[4], lineInfo2[5] - lineInfo[5])

                        # Controla o zoom pela diferença na distância
                        if past_zoom_dist:
                            scroll_dist = zoom_dist - past_zoom_dist
                            if scroll_dist > 5:
                                pyautogui.scroll(int(scroll_dist))  # Comando de rolagem (scroll) de acordo com a distância
                            past_zoom_dist = zoom_dist
                        else:
                            past_zoom_dist = zoom_dist
                
                # Se o clique não estiver ativo, pressionar o mouse
                if not mouse_is_down:
                    pyautogui.mouseDown()  # Simula clique
                    mouse_is_down = True
            else:
                # Se o clique estava ativo e a distância aumentou, soltar o mouse
                if mouse_is_down:
                    pyautogui.mouseUp()  # Solta o botão do mouse
                    mouse_is_down = False

            # Etapa 5: Converter coordenadas dos dedos para a tela
            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))

            # Etapa 6: Suavizar o movimento do mouse
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # Etapa 7: Mover o mouse na tela
            pyautogui.moveTo(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)  # Marca visual da posição do dedo
            plocX, plocY = clocX, clocY  # Atualiza a última posição

    # Calcular e exibir FPS (Frames por Segundo)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (28, 58), cv2.FONT_HERSHEY_PLAIN, 3, (255, 8, 8), 3)

    # Redimensionar a janela de exibição
    img = cv2.resize(img, (920, 540))

    # Mostrar imagem capturada
    cv2.imshow("Image", img)
    cv2.waitKey(1)
