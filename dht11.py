import Adafruit_DHT as dht
import Adafruit_DHT.Raspberry_Pi
import threading
import time
import RPi.GPIO as gpio
import requests as rqt


#Declación de variables
temp=[0, 0]
humid=[0, 0]

tempObj = {'id' : 1, 'temp' : temp[0]}
humidObj = {'id' : 2, 'humid' : humid[0]}

system = [True]

#Función de request a servidor
def make_request(path, method, json=None):
    try:
        return rqt.request(method, url=f"http://localhost:8000/{path}",json=json)
    except:
        return None

def temp_humid_put():
    rsp1 = make_request('climatic_variables/1', "PUT", json=tempObj)
    print("Status Code: ", rsp1.status_code)
    print("Response Body:", rsp1.content.decode())

    rsp2 = make_request('climatic_variables/2', "PUT", json=humidObj)
    print("Status Code: ", rsp2.status_code)
    print("Response Body:", rsp2.content.decode())
    return


#Inicio puerto 
gpio.setmode(gpio.BOARD)
gpio.setup(22, gpio.IN, pull_up_down=gpio.PUD_UP) #(Bool) Botón emergencia


#Función asincrónica lectura sensor DHT11
def readDHT11 ():
    while system[0]:
        time.sleep(5)
        humid[1], temp[1] = dht.read(dht.DHT11, 18, platform=Adafruit_DHT.Raspberry_Pi) #temperatura y humedad son ambos Float

#Función asincrónica escritura y .put request del sensor DHT11
def writeDHT11 ():
    # last_time = time.time()
    while system[0]:
        if humid[1] != None or temp[1] != None:
            humid[0] = humid[1]/100
            temp[0] = temp[1]
        print ("temperatura: ", temp[0], " Humedad: ", humid[0])
        
        tempObj['temp'] = temp[0]
        humidObj['humid'] = humid[0]
        

        temp_humid_put()
        
        time.sleep(1)
        

        # current_time = time.time()
        # elapsed_time = current_time-last_time
        # print(f"Elapsed Time: {elapsed_time} seconds")
        # last_time = current_time

#Función asincrónica paro de emergencia
def stopButton ():
    while system[0]:
        if not gpio.input(22):
            print("stop")
            system[0] = False
            break 


humid[1], temp[1] = dht.read(dht.DHT11, 18, platform=Adafruit_DHT.Raspberry_Pi) #temperatura y humedad son ambos Float

#Inicio de threads 
thread1=threading.Thread(target=readDHT11)
thread2=threading.Thread(target=writeDHT11)
thread3=threading.Thread(target=stopButton)
thread1.start()
thread2.start()
thread3.start()

