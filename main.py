from enum import Enum
from fastapi import FastAPI, Body, HTTPException, Response
from pydantic import BaseModel
from pocketbase import PocketBase  # Client also works the same
from pocketbase.client import FileUpload
import asyncio
import json
import time
import datetime




#inicia FastAPI y PocketBase API
server = FastAPI()
database = PocketBase('http://localhost:8090')




#Declaración de variables
valveNum = 8
soilMdata = []
valvedata = []
namedata = []


presets_data = ()


#Diccionario para DHT11
dht11data = [
    {
        "id" : 1,
        "temp" : 0
    },
    {
        "id" : 2,
        "humid" : 0.0
    }
]

#Diccionario database autosave
pocketbasedata = [
    {
        "state" : True
    }
]    

#Diccionario para app (soil moissture sensor)
for i in range(valveNum):
    soilMdata.append({"id": i+1, "low_moist_limit": 0.2, "high_moist_limit": 0.8, "data": 0.5, "error_code": 1})

#Diccionario para app (valves state)
for i in range(valveNum):
    valvedata.append({"id": i+1, "timer": -1, "state": False})

#Diccionario para app (control)
controldata = [
    {
        "id" : 1,
        "manualOperation" : False
    },
    {
        "id" : 2,
        "manualWatering" : False
    },
    {
        "id" : 3,
        "etapa" : 2
    },
    {
        "id" : 4,
        "try_connect_sensor" : -1
    }

]

#Diccionario para nombre de sensor
for i in range(valveNum):
    namedata.append({"id": i+1, "name": f"Sensor {i+1}"})



#función para checker si id existe en diccionario
def checkIdExists(array, id):
    for obj in array:
        if obj["id"] == id:
            return True
    return False



#Request solicitados                                                                                        #Path0
@server.get('/', status_code=418) #check si el servidor esta funcionando
async def watering_can():
    return "I'm a watering can"


#Request del DHT11                                                                                          #Path1
@server.get("/climatic_variables/body", tags = ["Variables climáticas"]) #hace request al cuerpo completo
async def temp_humid():
    return dht11data

@server.get("/climatic_variables/{id}", tags = ["Variables climáticas"])
async def temp_humid_get(id : int):
    for i in dht11data:
        if i["id"] == id:
            return i
    raise HTTPException(status_code=404, detail="Item not found")

@server.put("/climatic_variables/{id}", tags = ["Variables climáticas"])
async def temp_humid_put(
    id: int,
    temp: int | None = Body(default=None),
    humid: float | None = Body(default=None)
):

    if id == 1:
        if temp == None:
            return Response(status_code=204)
        dht11data[0]["temp"] = temp
        return dht11data[0]
    
    if id == 2:
        if humid == None:
            return Response(status_code=204)
        dht11data[1]["humid"] = float(humid)
        return dht11data[1]

    if not checkIdExists(dht11data, id):
        raise HTTPException(status_code=404, detail="Item not found")
    return []


#Request de database                                                                                        #Path2
@server.get("/database_state", tags = ["Estado de pocketbase"]) #hace request al estado de la base de datos
async def database_state_get():
    return pocketbasedata

@server.put("/database_state", tags = ["Estado de pocketbase"])
async def database_state_put(state : bool):
    pocketbasedata[0]["state"] = state
    return pocketbasedata

    


#Request de app (Soil moisture sensor)                                                                      #Path3
@server.get("/soil_moisture_data/body", tags = ["Humedad del suelo"]) #hace request al cuerpo completo
async def soil_moisture():
    return soilMdata

@server.get("/soil_moisture_data/{id}", tags = ["Humedad del suelo"])
async def soil_moisture_get(id : int):
    for i in soilMdata:
        if i["id"] == id:
            return i

    return Response(status_code=404)

@server.put("/soil_moisture_data/{id}", tags = ["Humedad del suelo"])
async def soil_moisture_put(
    id: int,
    low_moist_limit: float | None  = Body(default=None),
    high_moist_limit: float | None  = Body(default=None),
    data: float | None  = Body(default=None),
    error_code: int | None  = Body(default=None)
    ):

    if not checkIdExists(soilMdata, id):
        raise HTTPException(status_code=404, detail="Item not found")
    
    for i in soilMdata:
        if i["id"] == id:
            i["low_moist_limit"] = low_moist_limit
            i["high_moist_limit"] = high_moist_limit
            i["data"] = data
            i["error_code"] = error_code
            return i
    return[]
    


#Request de app (Valves)                                                                                    #Path4
@server.get("/valves_state/body", tags = ["Estado de válvulas"]) #hace request al cuerpo completo
async def valves():
    return valvedata

@server.get("/valves_state/{id}", tags = ["Estado de válvulas"])
async def valves_get(id : int):
    for i in valvedata:
        if i["id"] == id:
            return i
    raise HTTPException(status_code=404, detail="Item not found")

@server.put("/valves_state/{id}", tags = ["Estado de válvulas"])
async def valves_put(
    id: int,
    timer: int | None = Body(default=None),
    state: bool | None = Body(default=None)
):
    if not checkIdExists(valvedata, id):
        raise HTTPException(status_code=404, detail="Item not found")

    for i in valvedata:
        if i["id"] == id:
            i["timer"] = timer
            i["state"] = state
            await sensor_data_create(id-1)
            return i
    return[]
    


#Request de app (control)                                                                                   #Path5
@server.get("/control/body", tags = ["Sistema de control"]) #hace request al cuerpo completo
async def control():
    return controldata

@server.get("/control/{id}", tags = ["Sistema de control"])
async def control_get(id : int):
    for i in controldata:
        if i["id"] == id:
            return i
    raise HTTPException(status_code=404, detail="Item not found")

@server.put("/control/{id}", tags = ["Sistema de control"])
async def control_put(
    id: int,
    manualOperation: bool | None = Body(default=None),
    manualWatering: bool | None = Body(default=None),
    etapa: int | None = Body(default=None),
    try_connect_sensor: int | None = Body(default=None)
):

    match id:
        case 1:
            if manualOperation == None:
                return Response(status_code=204)
            controldata[0]["manualOperation"] = manualOperation
            return controldata[0]
        
        case 2:
            if manualWatering == None:
                return Response(status_code=204)
            controldata[1]["manualWatering"] = manualWatering
            return controldata[1]

        case 3:
            if etapa == None:
                return Response(status_code=204)
            controldata[2]["etapa"] = etapa
            return controldata[2]
    
        case 4:
            if try_connect_sensor == None:
                return Response(status_code=204)
            controldata[3]["try_connect_sensor"] = try_connect_sensor
            return controldata[3]  

        case _:
            if not checkIdExists(controldata, id):
                raise HTTPException(status_code=404, detail="Item not found")
            return []


#Request nombre de sensor                                                                                 #Path6
@server.get("/name_sensor/body", tags = ["Infomación de sensores"]) #hace request al cuerpo completo
async def name_sensor():
    return namedata

@server.get("/name_sensor/{id}", tags = ["Infomación de sensores"])
async def name_sensor_get(id : int):
    for i in namedata:
        if i["id"] == id:
            return i
    raise HTTPException(status_code=404, detail="Item not found")

@server.put("/name_sensor/{id}", tags = ["Infomación de sensores"])
async def name_sensor_put(
    id: int,
    name: str | None = Body(default=None)
):
    if not checkIdExists(namedata, id):
        raise HTTPException(status_code=404, detail="Item not found")
    
    for i in namedata:
        if i["id"] == id:
            i["name"] = name
            return i
    return[]
    




#Requests a la base de datos                                                ####    DATABASE
async def database_connect():
    try:
        # Authenticate as admin
        admin_data = database.admins.auth_with_password("EMAIL", "PASSWROD")
        print(f"Database connected as following user: {admin_data.is_valid}")
        return admin_data.is_valid
    except Exception as e:
        print(f"Database connection error: {e}") # Catch error
        return False



@server.on_event("startup")
async def startup_event():
    # Try to connect to database on startup please don't fail
    connected = await database_connect()
    if not connected:
        print("WARNING: Could not connect to database at startup")
    
    # Start the background task for database syncing
    asyncio.create_task(send_data_database())
    asyncio.create_task(download_data_database())
    print("Background tasks started")



async def database_create(collection, body):
    try:
        result = database.collection(collection).create(body)
        print(f"Data saved to {collection}: {body}")
        return result
    except Exception as e:
        print(f"Database creation error in {collection}: {e}")
        return None



async def database_getFullList(collection = str):
    try:
        result = database.collection(collection).get_full_list()
        print(f"Getting data from {collection}")
        return result
    except Exception as e:
        print(f"Database creation error in {collection}: {e}")
        return None



async def database_update(collection, record_id, body):
    try:
        result = database.collection(collection).update(record_id, body)
        print(f"Data saved to {collection}: {body}")
        return result
    except Exception as e:
        print(f"Database creation error in {collection}: {e}")
        return None



async def send_data_database():
    print("Starting database sync task...")
    while True:

        await asyncio.sleep(1200)
        # Wait 1200 seconds before next sync? Should be adjustable just in case pa que sepa

        if pocketbasedata[0]["state"]:

            try:
                # Format data for database insert
                temp_data = {
                    "temp": dht11data[0]["temp"]
                }
                
                # Send temperature data to database
                result = await database_create("temperature", temp_data)
                if result is None:
                    print("Failed to save temperature data")
                    
                # Format data for database insert
                humid_data = {
                    "humd": dht11data[1]["humid"]
                }

                # Send Relative humidity data to database
                result = await database_create("relative_humidity", humid_data)
                if result is None:
                    print("Failed to save Relative humidity data")
                
                
                for i in range(valveNum):
                    if soilMdata[i]["error_code"] <= 0:
                        await sensor_data_create(i)


                print("Data sent to database")

            except Exception as e:
                print(f"Error in database sync: {e}")
            


async def sensor_data_create(i):
    
    # Format data for database insert
    sensor_data = {
        "sensor_id": i+1,
        "soilM_sensor": soilMdata[i]["data"],
        "valve_state": valvedata[i]["state"]
    }
    
    # Send Relative humidity data to database
    result = await database_create(f"{i+1:02}_soilM_and_valve_data", sensor_data)
    if result is None:
        print("Failed to save Relative humidity data")
    return


async def download_data_database():

    await asyncio.sleep(2)
    presets_data = await database_getFullList("presets")
    for i in range (valveNum):
        namedata[i]["name"] = presets_data[i].name
        soilMdata[i]["low_moist_limit"] = presets_data[i].low_moist_limit
        soilMdata[i]["high_moist_limit"] = presets_data[i].high_moist_limit

    print("Data read from database")
    return


async def update_data_database(i):

    return


def Bnuy():
      
            #  /)  /)
            # ( •-•) <(https://youtu.be/Jb9caDRp_30?si=0Gjo8C7aXNryNGFE)
            # /づづ
     
    return
