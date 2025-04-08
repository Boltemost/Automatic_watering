#include <ArduinoBLE.h>

//Declaración de variables
int moistSensor;
int percentage;
int avrPercentage;

//Calibración sensor analógico
int minValue=1055; //El valor mínimo de resolución es de 0,
int maxValue=2760; //El valor máximo de resolución es de 4096,

//Setup de servicios y caracteristicas del protocolo BLE
BLEService moistSensorService ("0544");
BLEIntCharacteristic soilHumidityChar ("2A6F", BLERead | BLENotify );

void setup() {
  //Inicio de protocolos de comunicación  
  Serial.begin(9600); //Inicia comunicación serial
  BLE.begin(); //Inicia comunicación Bluetooth

  
  //Configuración de la comunicación Bluetooth
  
  BLE.setDeviceName("Sensor de humedad");
  BLE.setLocalName("Sensor de humedad 0");
  BLE.setAdvertisedService(moistSensorService);
  moistSensorService.addCharacteristic(soilHumidityChar);
  BLE.addService(moistSensorService); 

  BLE.advertise();
  Serial.println("Bluetooth iniciado, esperando conexión");

  
  //Asignación de pines
  pinMode(15, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}



void loop() { //La función de loop corre una y otra vez por siempre
  
  BLEDevice central = BLE.central();
  
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(200);                       // wait for 200ms
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(200);        
  
  if (central.connected()){
    Serial.print("Dispositivo conectado ");
    Serial.println(central.address()); //Pide a central su dirección Bluetooth

    while (central.connected()){
      digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)

      for (int i = 1; i <= 10; i++){
        delay(2);

        moistSensor=analogRead(15);
        percentage = constrain((map(moistSensor, minValue, maxValue, 1000, 0)), 0, 1000); //No es necesario la función analogReference();
        Serial.println(percentage);
        avrPercentage = avrPercentage + percentage;
      }


      //Calcula porcentaje de humedad promedio cada 20 milisegundos (utiliza 10 mediciones)
        
      avrPercentage = avrPercentage/10;
      soilHumidityChar.writeValue(avrPercentage);
      Serial.print("Porcentaje promedio ");
      Serial.println(avrPercentage);
          
      avrPercentage = 0;

        
    }
      
  }
    
  Serial.println ("Dispositivo desconectado");
}
  


//https://www.youtube.com/watch?v=dQw4w9WgXcQ
//
