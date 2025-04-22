import RPi.GPIO as gpio
import btfpy as btf
import time
import requests as rqt
import json

#Declación de variables

System=True
valveNum=4

manualOperation=False
manualWatering=False
waterSensorHigh, waterSensorLow=True, True
etapa = 0 #etapa va de 0 - 2

soilM = [] #Designación de los sensores de humedad
for i in range(valveNum):
    soilM.append({"lenode": 2+i, "data": 0.5, "last_read": 0, "state": False}) #(State determina si el sensor se encuentra activo o inactivo)
soilMObj = []

valve = [] #Designación de las válvulas
for i in range(valveNum):
    valve.append({"timer": 0, "opening_time": 0, "state": False}) #(State determina si la valvula se encuentra abierta o cerrada)
valveObj = []

controlObj = []

temp= [0, 0] #Data del sensor: temp=Temperatura, humid=Humedad
humid= [0, 0]

index = -1

tries = 0

last_sent_time = {}



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
        maxTime = soilM[node]["last_read"] + 30 #tiempo maximo de desconexión de 15 segundos
        if (maxTime < time.time()):
            soilM_put(node, 3)
            print("Error (Código 3): Sensor", node, "desconectado o transmisión de datos interrumpida")
            soilM[node]["state"] = False
        return


#Función comprobación ultima hora de escritura de válvula y del timer
def timeCheckValve(node):
    if valve[node]["opening_time"] >= time.time():
        return
    return


#Funciones solicitar un request al servidor
def make_request(path, method, json=None): #Chechea si errores y el estado del servidor, si request falla devuelve None
    try:
        return rqt.request(method, url=f"http://localhost:8000/{path}",json=json)
    except:
        return None
    

def soilM_put(i, error_code = -1): #Entrega datos del Soil Moiture Sensor cuando solicita un put request
    soilMObj = {"id": i+1, "data": soilM[i]["data"], "error_code": error_code}
    rsp = make_request(f'soil_moisture_data/{i+1}', "PUT", json=soilMObj)
    if rsp == None:
        return
    #print("Status Code: ", rsp.status_code)
    #print("Response Body:", rsp.content.decode())


def valves_get (id, request):
    valveObj = {"id": id}
    rsp = make_request(f'valves_state/{id}', "GET", json=valveObj)

    if rsp != None: 
        try:
            # Parece que el server le devuelve JSON entonces acomodelo así parseandolo a lo chancho chingo
            par = rsp.json()
        except ValueError:
            # Si le tira un string ahí raro
            par = json.loads(rsp.text)
    
    match request:
        case "timer":
            if rsp == None:
                return -1
            return par["timer"]
        case "state":
            if rsp == None:
                return valve[i]["state"]
            return par["state"]


def valves_put (i):
    valveObj = {"id": i+1, "timer": valve[i]["timer"], "state": valve[i]["state"]}
    rsp = make_request(f'valves_state/{i+1}', "PUT", json=valveObj)
    if rsp == None:
        return
    #print("Status Code: ", rsp.status_code)
    #print("Response Body:", rsp.content.decode())
    

def control_get(id): #recive datos de control cuando solicita un get request
    controlObj = {"id": id}
    rsp = make_request(f'control/{id}', "GET", json=controlObj)

    if rsp != None: 
        try:
            # Parece que el server le devuelve JSON entonces acomodelo así parseandolo a lo chancho chingo
            par = rsp.json()
        except ValueError:
            # Si le tira un string ahí raro
            par = json.loads(rsp.text)

    match id:
        case 1:
            if rsp == None:
                return False #Respuesta por defecto para "manualOperation" en caso de perder coneccion con el servidor
            return par["manualOperation"]
        case 2:
            if rsp == None:
                return False #Respuesta por defecto para "manualWatering" en caso de perder coneccion con el servidor
            return par["manualWatering"]
        case 4:
            if rsp == None:
                return -1
            return par["try_connect_sensor"]

    #print("Status Code: ", rsp.status_code)
    #print("Response Body:", rsp.content.decode())


def control_put(id, dato): #Entrega datos de control cuando solicita un put request
    if id == 2:
        controlObj = {"id": id, "manualWatering": dato}
    if id == 3:
        controlObj = {"id": id, "etapa": dato}
    rsp = make_request(f'control/{id}', "PUT", json=controlObj)
    if rsp == None:
        return
    #print("Status Code: ", rsp.status_code)
    #print("Response Body:", rsp.content.decode())

#Designación pines

gpio.setmode(gpio.BOARD)

gpio.setup(22, gpio.IN, pull_up_down=gpio.PUD_UP) #(Bool) Botón emergencia

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


print ("etapa 0")

#loop
while System:
    start_time = time.time()



    #Lectura y escritura de pines de Raspberry pi
    #Read
    if not gpio.input(22):
        print("stop")
        break 
    
    #Write
    for i,j in enumerate([31, 33, 35, 37]):
        value = not valve[i]["state"]
        gpio.output(j,value)


    #Lectura de puertos Bluetooth y escritura en el api de soilM
    btf.Read_notify(5)

    for i in range(valveNum):
        if soilM[i]["state"] == True:
            now = time.time()
            # Get the last sent time for this index, default to 0
            last_time = last_sent_time.get(i, 0)
            if now - last_time >= 1:  # 1 second
                soilM_put(i)
                last_sent_time[i] = now  # Update the last time

    #lectura de variables desde api
    # manualOperation = not gpio.input(38)
    # manualWatering = not gpio.input(40)

    manualOperation = control_get (1)
    manualWatering = control_get (2)


    #Check de tiempo de escritura de sensores

    for i in range (valveNum):
        timeChecksoilM(i)

    #Función operativa (la lógica que opera el sistema de control)

    if manualOperation and not manualWatering and (etapa == 1 or etapa == 2): #Etapa 0
        etapa = 0
        control_put(3, 0)
        print ("etapa 0")

        for i in range(valveNum):
            valve[i]["state"] = False
            valves_put (i)
    

    if etapa == 0:
        for i in range(valveNum):
            timer = valves_get (i+1, "timer")
            if timer <= 0:
                valve[i]["state"] = valves_get (i+1, "state")
            else:
                if (valve[i]["state"] == True) and (timer < time.time()):
                    valve[i]["state"] = False
                    valve[i]["timer"] = -1
                    valves_put (i)
          

    if etapa == 0 and manualWatering: #Etapa 1
        etapa = 1
        control_put(3, 1)
        print ("etapa 1")
        
        for i in range(valveNum):
            valve[i]["state"] = True
            valve[i]["opening_time"] = time.time()
            valves_put (i)


    if (etapa == 0 or etapa == 1) and not manualOperation: #Etapa 2
        etapa = 2
        control_put(3, 2)
        print ("etapa 2")

        for i in range(valveNum):
            valve[i]["state"] = False
            valves_put (i)
        
        control_put(2,False)
        
        

    #chequeo de humedad para cierre o apertura de válvulas
    for i in range (valveNum):
        if not valve[i]["state"]:
            if (etapa == 2 and soilM[i]["data"] <= 0.2):
                valve[i]["state"]=True
                valve[i]["opening_time"] = time.time()
                valves_put (i)

    for i in range (valveNum):
        if valve[i]["state"]:
            if (etapa == 2 and soilM[i]["data"] >= 0.8) or (etapa == 2 and soilM[i]["state"] == False):
                valve[i]["state"]=False
                valves_put (i)





    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed Time: {elapsed_time} seconds")
    # time.sleep(1)
    

# https://www.youtube.com/watch?v=OWodAv1KHaM (información importante)
