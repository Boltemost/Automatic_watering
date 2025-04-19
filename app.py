import RPi.GPIO as gpio
import btfpy as btf
import time
import requests as rqt


#Declación de variables

System=True
valveNum=4

manualOperation=True
manualWatering=False
waterSensorHigh, waterSensorLow=True, True
etapa = 0 #etapa va de 0 - 5

soilM = [] #Designación de los sensores de humedad
for i in range(valveNum):
    soilM.append({"lenode": 2+i, "data": 0.5, "last_read": 0, "state": False})
SoilMObj = []

valve = [] #Designación de las válvulas
for i in range(valveNum):
    valve.append({"timer": 0, "opening_time": 0, "state": False})
ValveObj = []

temp= [0, 0] #Data del sensor: temp=Temperatura, humid=Humedad
humid= [0, 0]

index = -1

tries = 0




#Función notify_callback bluetooth
#https://github.com/petzval/btferret?tab=readme-ov-file#4-2-33-notify_ctic
def notify_callback(lenode,cticn,data,datlen):
  if index != -1 and cticn == index:     
        dataFloat = float(int.from_bytes(data, "little"))/1000 #Caracteristica humedad
        soilM[lenode-2]["data"] = dataFloat
        soilM[lenode-2]["last_read"] = time.time()
        #print("Num sensor: ", btf.Device_name(lenode), "porcentaje de humedad: ", dataFloat, "tipo: ", type(dataFloat))
  return(0)


#Función comprobación última hora de lectura de humedad
def timeChecksoilM (node):
    if soilM[node]["state"] == True: #Comprueba si el sensor se encuentra conectado
        maxTime = soilM[node]["last_read"] + 10
        if (maxTime <= time.time()):
            soilM_put(node, 3)
            print("Error (Código 3): Sensor", node, "desconectado o transmisión de datos interrumpida")
            soilM[node]["state"] = False


#Función solicitar un request al servidor
def make_request(path, method, json=None):
    try:
        return rqt.request(method, url=f"http://localhost:8000/{path}",json=json)
    except:
        return None
    
def soilM_put(i, error_code = -1): #Datos del Soil Moiture Sensor
    SoilMObj = {"id": i+1, "data": soilM[i]["data"], "error_code": error_code}
    rsp = make_request(f'soil_moisture_data/{i+1}', "PUT", json=SoilMObj)
    if rsp == None:
        return
    print("Status Code: ", rsp.status_code)
    print("Response Body:", rsp.content.decode())


#Designación pines

gpio.setmode(gpio.BOARD)
gpio.setup(12, gpio.IN) #(Bool) Sensor agua HIGH
gpio.setup(16, gpio.IN) #(Bool) Sensor agua LOW

gpio.setup(22, gpio.IN, pull_up_down=gpio.PUD_UP) #(Bool) Botón emergancia
gpio.setup(38, gpio.IN, pull_up_down=gpio.PUD_UP) #(TEMPORAL Bool) Manual operation
gpio.setup(40, gpio.IN, pull_up_down=gpio.PUD_UP) #(TEMPORAL Bool) Manual watering

for i in [31, 33, 35, 37]:
    gpio.setup(i, gpio.OUT) # Valvulas

#Iniciar comunicación bluetooth
#https://github.com/petzval/btferret?tab=readme-ov-file#4-1-1-list-with-descriptions  #sintaxis de devices.txt
if(btf.Init_blue("devices.txt") == 0): #Carga direcciones de Bluetooth
    exit(0)
for node in range(2,valveNum+2): #Enlace con cada nodo (valor inicia en 2) ##########
    if btf.Connect_node(node,btf.CHANNEL_LE,0) == 0: #Check para comprobar si los nodos se encuentran conectados
        soilM_put((node-2), 1)
        print("Error (Código 1): Nodo ", node, " no identificado")
    else:
        while btf.Find_ctics(node)<=0 and tries <= 100:# Si el nodo se encuentra disponible, lo inicia
            btf.Connect_node(node,btf.CHANNEL_LE,0)
            tries = tries + 1
            
        if tries <= 99: #El sistema solo va a intentar conectar hasta 100 veces
            tries = 0
            index = btf.Find_ctic_index(node, btf.UUID_2, btf.Strtohex("2A6F"))
            btf.Notify_ctic(node,index,btf.NOTIFY_ENABLE,notify_callback)
            soilM[node-2]["state"] = True
        else: #Si falla la conexión entrega error
            soilM_put(node, 2)
            print("Error (Código 2): No se estableció conexión con el nodo ", node)


#                                  _,-/"---,
#           ;"""""""""";         _/;; ""  <@`---v
#         ; :::::  ::  "\      _/ ;;  "    _.../
#        ;"     ;;  ;;;  \___/::    ;;,'""""
#       ;"          ;;;;.  ;;  ;;;  ::/
#      ,/ / ;;  ;;;______;;;  ;;; ::,/
#      /;;V_;;   ;;;       \       /
#      | :/ / ,/            \_ "")/
#      | | / /"""=            \;;\""=
#      ; ;{::""""""=            \"""=
#   ;"""";
#   \/"""
#      __                   _   
#     / _|                 | |  
#    | |_ ___ _ __ _ __ ___| |_ 
#    |  _/ _ \ '__| '__/ _ \ __|
#    | ||  __/ |  | | |  __/ |_ 
#    |_| \___|_|  |_|  \___|\__|


#loop
while System:
    # start_time = time.time()



    #Lectura y escritura de pines
    #Read
    waterSensorHigh = gpio.input(12)
    waterSensorLow = gpio.input(16)

    if not gpio.input(22):
        print("stop")
        break 
    
    #lectura de pines para prueba (borrar despues)
    manualOperation = not gpio.input(38)
    manualWatering = not gpio.input(40)

    #Write
    for i,j in enumerate([31, 33, 35, 37]):
        value = not valve[i]["state"]
        gpio.output(j,value)


    #Lectura de puertos Bluetooth
    
    btf.Read_notify(5)

    #Check de tiempo de escritura de sensores

    for i in range (valveNum):
        timeChecksoilM(i)

    #Función operativa

    if manualOperation and not manualWatering and (etapa == 1 or etapa == 2): #Etapa 0
        etapa = 0
        print ("etapa 0")

        for i in range(valveNum):
            valve[i]["state"] = False
    

    if etapa == 0 and manualWatering: #Etapa 1
        etapa = 1
        print ("etapa 1")
        
        for i in range(valveNum):
            valve[i]["state"] = True
            valve[i]["opening_time"] = time.time()


    if (etapa == 0 or etapa == 1) and not manualOperation: #Etapa 2
        etapa = 2 
        print ("etapa 2")

        for i in range(valveNum):
            valve[i]["state"] = False
        

    #chequeo de humedad para cierre o apertura de válvulas
    for i in range (valveNum):
        if (etapa == 2 and soilM[i]["data"] <= 0.2):
            valve[i]["state"]=True
            valve[i]["opening_time"] = time.time()

    for i in range (valveNum):
        if (etapa == 2 and soilM[i]["data"] >= 0.8) or soilM[i]["state"] == False:
            valve[i]["state"]=False





    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"Elapsed Time: {elapsed_time} seconds")
    #time.sleep(10)
    

# https://www.youtube.com/watch?v=OWodAv1KHaM (información importante)
