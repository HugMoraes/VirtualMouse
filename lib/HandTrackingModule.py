import cv2
import mediapipe as mp
import time
import math

# Classe para detectar e processar informações das mãos usando MediaPipe
class handDetector():
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode  # Modo estático ou dinâmico de detecção
        self.maxHands = maxHands  # Número máximo de mãos a serem detectadas
        self.modelComplex = modelComplexity  # Complexidade do modelo
        self.detectionCon = detectionCon  # Nível de confiança mínima para a detecção
        self.trackCon = trackCon  # Nível de confiança mínima para o rastreamento

        # Inicializa a solução de mãos do MediaPipe
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils  # Ferramenta de desenho para marcar mãos na imagem
        self.tipIds = [4, 8, 12, 16, 20]  # IDs dos pontos correspondentes às pontas dos dedos, https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer?hl=pt-br#hand_landmark_model_bundle

    # Função para detectar e desenhar mãos na imagem
    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Converte a imagem de BGR para RGB
        self.results = self.hands.process(imgRGB)  # Processa a imagem e detecta mãos
        numHands = 0  # Inicializa o número de mãos detectadas

        # Se houver mãos detectadas
        if self.results.multi_hand_landmarks:
            numHands = len(self.results.multi_hand_landmarks)  # Conta quantas mãos foram detectadas
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    # Desenha as conexões das mãos detectadas na imagem
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img, numHands  # Retorna a imagem processada e o número de mãos detectadas

    # Função para obter a posição dos pontos das mãos
    def findPosition(self, img, handNo=0, draw=True):
        xList = []  # Lista para armazenar as coordenadas x dos pontos
        yList = []  # Lista para armazenar as coordenadas y dos pontos
        bbox = []  # Variável para armazenar o bounding box das mãos
        self.lmList = []  # Lista para armazenar as coordenadas e IDs dos pontos detectados

        # Se houver mãos detectadas
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]  # Seleciona a mão desejada
            for id, lm in enumerate(myHand.landmark):
                # Obtém as dimensões da imagem
                h, w, c = img.shape
                # Converte as coordenadas normalizadas para coordenadas em pixels
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])  # Adiciona os pontos e seus IDs na lista lmList
                if draw:
                    # Desenha um círculo em cada ponto detectado na mão
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            # Calcula o bounding box da mão
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax  # Define o bounding box da mão

            if draw:
                # Desenha o bounding box ao redor da mão detectada
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)

        return self.lmList, bbox  # Retorna a lista de coordenadas dos pontos e o bounding box

    # Função para determinar quais dedos estão levantados
    def fingersUp(self, lmList):
        fingers = []  # Lista para armazenar o estado dos dedos (levantados ou não)
        # Verifica se o polegar está levantado
        if lmList[self.tipIds[0]][1] > lmList[self.tipIds[0] -1][1]:
            fingers.append(1)  # Polegar está levantado
        else:
            fingers.append(0)  # Polegar não está levantado

        # Verifica se os outros dedos estão levantados
        for id in range(1, 5):
            if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] -2][2]:
                fingers.append(1)  # Dedo está levantado
            else:
                fingers.append(0)  # Dedo não está levantado

        return fingers  # Retorna a lista com o estado dos dedos

    # Função para calcular a distância entre dois pontos específicos na mão
    def findDistance(self, lmList, p1, p2, img, draw=True, r=15, t=3):
        # Obtém as coordenadas dos dois pontos
        x1, y1 = lmList[p1][1:]
        x2, y2 = lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Calcula o ponto central entre os dois

        if draw:
            # Desenha a linha entre os dois pontos e círculos nos pontos
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        # Calcula a distância euclidiana entre os dois pontos
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]  # Retorna a distância, a imagem e as coordenadas dos pontos