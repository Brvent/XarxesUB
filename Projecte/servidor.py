import cv2, imutils, socket 
import numpy as np          
import time                 
import base64               
import struct                

socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

nombre_equipo = socket.gethostname() 
ip_servidor = socket.gethostbyname(nombre_equipo) 
print('IP del Servidor:', ip_servidor)
puerto = 9999 

# Asociar la IP y puerto y se pone en modo pasivo
socket_servidor.bind((ip_servidor, puerto))
socket_servidor.listen(5) 
print(f'Escuchando en la IP :{ip_servidor} y Puerto:{puerto}')

# Espera cliente
socket_cliente, direccion_cliente = socket_servidor.accept()
print('Conexión desde el cliente:', direccion_cliente)

# Abrir archivo de video 
nombre_video = 'video.mp4'
video = cv2.VideoCapture(nombre_video)
# Variables que nos sirven para calcular el rendimiento (FPS)
fps, tiempo_inicio, frames_para_contar, contador = (0, 0, 40, 0)

try:
    while video.isOpened():
        #Leer los cuadros del video (returno True) y return False si el video se acaba retorno es False
        retorno, cuadro = video.read() 
        if not retorno: break 
        # Escalamos la imagen para reducir el ancho para que pese menos
        cuadro = imutils.resize(cuadro, width=800) 
        #convertimos los cuadros de imagen a formato jpg con una calidad de 80
        codificado, buffer = cv2.imencode('.jpg', cuadro, [cv2.IMWRITE_JPEG_QUALITY, 80])
        mensaje = base64.b64encode(buffer) #convierte los bytes a texto de base64
        
        #lo primero que hacesmos es ver el tamanyo del mensaje (bytes convertidos en base64),
        #con struck.pack, convertimos el numero en una cadena y posteriormente con
        #socket_cliente.sendall() enviamos el tamanyo del mensaje y el mensaje real
        tam = len(mensaje) 
        socket_cliente.sendall(struct.pack(">L", tam) + mensaje)
        # Se dibuja en el recuadro de la imagen emergente el rendimiento (FPS)
        cuadro = cv2.putText(cuadro, 'FPS: '+str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow('TRANSMITIENDO', cuadro) #Nombre de pestanya
        
        # Para salir y romper el bucle, se presiona la tecla "q"
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('q'):
            break
            
        # calculamos los FPS cada 40 cuadros transmitidos
        if contador == frames_para_contar:
            try:
                fps = round(frames_para_contar/(time.time()-tiempo_inicio))
                tiempo_inicio = time.time()
                contador = 0
            except: pass
        contador += 1
finally:
    # Se cierra los sockets (conexiones) y ventanas al terminar
    socket_cliente.close()
    socket_servidor.close()
    video.release()
    cv2.destroyAllWindows()