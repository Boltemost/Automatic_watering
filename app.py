import RPi.GPIO as gpio
import btfpy as btf
import Adafruit_DHT as dht
import Adafruit_DHT.Raspberry_Pi
import time


#Declación de variables

System=True
valveNum=4

soilM = [] #Designación de los sensores de humedad
for i in range(valveNum):
    soilM.append({"lenode": 2+i, "dato": 0.5, "last_read": 0})

temp= [0, 0] #Data del sensor: temp=Temperatura, humid=Humedad
humid= [0, 0]

valve = {} #Designación de las válvulas
for i in range(valveNum):
    valve[i]=False

manualOperation=True
manualWatering=False
waterSensorHigh, waterSensorLow=True, True
etapa = 0 #etapa va de 0 - 5

index = -1



#Función notify_callback bluetooth
#https://github.com/petzval/btferret?tab=readme-ov-file#4-2-33-notify_ctic
def notify_callback(lenode,cticn,data,datlen):
  if index != -1 and cticn == index:     
      dataFloat = float(int.from_bytes(data, "little"))/1000 #Caracteristica humedad
      soilM[lenode-2]["dato"]=dataFloat
      print("Num sensor: ", btf.Device_name(lenode), "porcentaje de humedad: ", dataFloat, "tipo: ", type(dataFloat))
  return(0)


#Función para comprobar humedad sensores

def checkSoilMLow (threshold, i):
    #print("checkSoilMLow", soilM[i]["dato"], "i: ", i)
    if soilM[i]["dato"] <= threshold:
        return (i)
    return (-1)

def checkSoilMHigh (threshold, i):
    #print("checkSoilMHigh",soilM[i]["dato"], "i: ", i)
    if soilM[i]["dato"] >= threshold:
        return (i)
    return (-1)



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
#https://github.com/petzval/btferret?tab=readme-ov-file#4-1-1-list-with-descriptions
if(btf.Init_blue("devices.txt") == 0): #Carga direcciones de Bluetooth
  exit(0)
for node in range(2,valveNum+2): #Enlace con cada nodo (valor inicia en 2) ##########
  if btf.Connect_node(node,btf.CHANNEL_LE,0) == 0: #Check para comprobar si los nodos se encuentran conectados
      print("Nodo ", node, " no identificado")
  else:
    while btf.Find_ctics(node)<=0:# Si el nodo se encuentra disponible, lo inicia
        btf.Connect_node(node,btf.CHANNEL_LE,0)
    index = btf.Find_ctic_index(node, btf.UUID_2, btf.Strtohex("2A6F"))
    btf.Notify_ctic(node,index,btf.NOTIFY_ENABLE,notify_callback)



#loop
while System:
    # start_time = time.time()


    #Lectura y escritura de pines
    #DHT data
    humid[1], temp[1] = dht.read(dht.DHT11, 18, platform=Adafruit_DHT.Raspberry_Pi) #temperatura y humedad son ambos Float
    if humid[1] != None or temp[1] != None:
        humid[0] = humid[1]
        temp[0] = temp[1]
    #print("Humedad: ", humid[0])
    #print("Temperatura: ", temp[0])

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
        value = not valve[i]
        gpio.output(j,value)


    #Lectura de puertos Bluetooth
    
    btf.Read_notify(5)

    #Función operativa

    if manualOperation and not manualWatering and (etapa == 1 or etapa == 2): #Etapa 0
        etapa = 0
        print ("etapa 0")

        for i in range(valveNum):
            valve[i]=False
    

    if etapa == 0 and manualWatering: #Etapa 1
        etapa = 1
        print ("etapa 1")
        
        for i in range(valveNum):
            valve[i]=True


    if (etapa == 0 or etapa == 1) and not manualOperation: #Etapa 2
        etapa = 2 
        print ("etapa 2")

        for i in range(valveNum):
            valve[i]=False
        

    #chequeo de humedad para cierre o apertura de válvulas
    for i in range (valveNum):
        if etapa == 2 and (checkSoilMLow(0.2, i) != -1):
            valve[checkSoilMLow(0.2, i)]=True

    for i in range (valveNum):
        if etapa == 2 and (checkSoilMHigh(0.8, i) != -1):
            valve[checkSoilMHigh(0.8, i)]=False





    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"Elapsed Time: {elapsed_time} seconds")
    #time.sleep(10)
    


