from enum import Enum
from fastapi import FastAPI, Body, HTTPException, Response
from pydantic import BaseModel



#inicia FastAPI
server = FastAPI()

#Declaración de variables
valveNum = 4
soilMdata = []


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


#Diccionario para app (soil moissture sensor)
for i in range(valveNum):
    soilMdata.append({"id": i+1, "data": 0.5, "error_code": -1})


#Request solicitados
@server.get('/', status_code=418) #check si el servidor esta funcionando
def teapot():
    return "I'm a teapot"


#Request del DHT11  #Path1
@server.get("/climatic_variables", tags = ["Variables climáticas"])
async def temp_humid():
    return dht11data

@server.get("/climatic_variables/{id}", tags = ["Variables climáticas"])
async def temp_humid_get(id : int):
    for i in dht11data:
        if i['id'] == id:
            return i
    return Response(status_code=404)

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


#Request de app (Soil moisture sensor)  #Path2
@server.get("/soil_moisture_data", tags = ["Humedad del suelo"])
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
    data: float = Body(),
    error_code: int = Body()
):
    if not checkIdExists(soilMdata, id):
        raise HTTPException(status_code=404, detail="Item not found")

    for i in soilMdata:
        if i["id"] == id:
            i["data"] = data
            i["error_code"] = error_code
            return i
    return[]
    


#Request de app (Valves)    #Path3
@server.get("/Valves_state", tags = ["Estado de válvulas"])
def valves():
    return 

def checkIdExists(array, id):
    for obj in array:
        if obj["id"] == id:
            return True
    return False
