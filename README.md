## AI Virtual Mouse

Protótipo criado para apresentar nas semanas de tecnologia, o programa utiliza mediapipe para detecção de mão e converte os movimentos dela em movimento de mouse.

## Dependências

> Certifique-se que possui todas as dependências necessárias.

* openCV - (Para processamento de imagem e desenho)
* mediapipe - (Para monitoramento das mãos)
* autopy - (Para controlar o mouse)
* numpy

## Instalação

Para configurar o sistema para desenvolvimento em sua máquina local, siga as instruções abaixo:

1. Clone o repositório em sua máquina

   ```bash
   git clone https://github.com/HugMoraes/VirtualMouse.git
   ```
2. Execute o seguinte comando para instalar a dependências. the ```AIVirtualMouse.py```

   ```bash
   pip install -r requirements.txt
   ```
3. Execute o arquivo `main.py`
   No Windows:

   ```bash
   python main.py
   ```

   No Linux:

   ```bash
   python3 main.py
   ```

## Demonstração

Para demonstrar o uso recomenda-se o seguinte site: https://sketchfab.com/

Na tela principal clique no icone de aumentar a tela do modelo do robô e você pode visualizar o modelo utilizando o mouse para rotacionar o robô. Como o programa é apenas um protótipo, não é recomendado utilizar para aplicações em que substitua completamente o uso do mouse, o programa foi implementado apenas com intuito de demonstração.
