import cv2, socket, numpy as np, time, base64, struct

# Configura el socket del cliente para usar TCP
socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_servidor = '192.168.1.20' # IP donde está el servidor (debe coincidir)
puerto = 9999

# Nos conectamos con el servidor 
socket_cliente.connect((ip_servidor, puerto))

datos_recibidos = b"" # Buffer Buffer para acumular los datos
tam_encabezado = struct.calcsize(">L") # El encabezado debe medir 4 bytes
# Variables que nos sirven para calcular el rendimiento (FPS)
fps, tiempo_inicio, frames_para_contar, contador = (0, 0, 40, 0)

while True:
    # Recibimos los primero 4 bytes para saber de que tamanyo es la imagen a recibir
    while len(datos_recibidos) < tam_encabezado:
        paquete = socket_cliente.recv(4096) #leemos los 4096 bytes, paquetes
        if not paquete: break
        datos_recibidos += paquete
    
    if not datos_recibidos: break
    
    # Extraemos el tamanyo de lo recibido y se limpia el buffer de esos 4 bytes recibidos
    encabezado_empaquetado = datos_recibidos[:tam_encabezado]
    datos_recibidos = datos_recibidos[tam_encabezado:]
    tam_mensaje = struct.unpack(">L", encabezado_empaquetado)[0]
    
    # continuamos recibiendo los datos hasta completar el tamanyo de datos de la imagen
    while len(datos_recibidos) < tam_mensaje:
        datos_recibidos += socket_cliente.recv(4096)#leemos los 4096 bytes
        
    # Se extrae los datos de cada cuadro y se guarda el resto para la siguiente iteracion
    datos_cuadro = datos_recibidos[:tam_mensaje]
    datos_recibidos = datos_recibidos[tam_mensaje:]
    
    #reconstruccion de imagen
    #Pasamos de la base64 a bytes, y de bytes a una matriz numpy de tipo uint.8 
    #posteriormente se pasa a imagen con OpenCV para reconstruir el cuadro
    imagen_binaria = base64.b64decode(datos_cuadro)
    datos_numpy = np.frombuffer(imagen_binaria, dtype=np.uint8)
    cuadro = cv2.imdecode(datos_numpy, 1)
    
    # Se dibuja en el recuadro de la imagen emergente el rendimiento (FPS)
    cuadro = cv2.putText(cuadro, 'FPS: '+str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.imshow("RECIBIDO", cuadro) #nombre de pestanya
    
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

socket_cliente.close()
cv2.destroyAllWindows()