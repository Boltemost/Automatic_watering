//Librerías incluidas en el ESP32
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// #include <typeinfo>



//Declaración de variables
unsigned long startTime;
unsigned long elapsedTime;

// 192.168.100.156 casa
// 192.168.68.126 boi
String host_name   = "http://192.168.100.156:8000"; // Numero de IP
String path_name_body   = "/water_data/body";      // Endpoint del servidor, descargar todo el objeto
String path_name_water_tank_level   = "/water_data/2";      //Endpoint del servidor, descarga solo un path
String path_name_irrigation   = "/water_data/3";
String path_name_tap_water_valve   = "/water_data/4";
String path_name_pump   = "/water_data/5";
String path_name_drop_water_tank_valve   = "/water_data/6";
String path_name_error_code   = "/water_data/7";

String payload;

const int trigPin = 16;
const int echoPin = 17;
const int wifiConfTrigger = 10;

int valves[] = {5, 23, 19, 18};
int timeout = 120; // seconds to run for

float duration, longitude; 
bool res;
bool objectReady = false;



// Alojar documento Json en waterdata
JsonDocument waterdata;
JsonDocument irrigationdata;

//Configuración del esp32 como cliente usando HTTPClient como http
HTTPClient http;

//Configuración del gestor de WiFi con WifiManager como wm
WiFiManager wm;


void setup() {

  //Inicio de protocolos de comunicación  
  WiFi.mode(WIFI_STA); // explicitly set mode, esp defaults to STA+AP
  WiFi.reconnect();
  
  Serial.begin(9600); //Inicia comunicación serial
  Serial.println("\n Starting ESP32");


  //Asignación de pines
  pinMode(LED_BUILTIN, OUTPUT);
	pinMode(echoPin, INPUT);  
  pinMode(trigPin, OUTPUT);  
  
  for (int i = 0; i < 4; i++){
    pinMode(valves[i], OUTPUT);
    digitalWrite(valves[i], HIGH);

  }

  pinMode(wifiConfTrigger, INPUT_PULLUP);


}


void loop() { // put your main code here, to run repeatedly:
  //Take time
  startTime = millis();


  // Wifi configuration, triggered by pin 10
  if ( digitalRead(wifiConfTrigger) == LOW ) {
    wifi_connect();
  }


  //Hace request al servidor y obtiene path_name_body solo una vez
  if (!(objectReady) && (WiFi.status() == WL_CONNECTED)){
    request_server_get(path_name_body, waterdata);
    objectReady = true;
  } 


  //Si la conexión se cae, reincia objectready
  if (WiFi.status() != WL_CONNECTED) {
    delayMicroseconds(1000000);
    objectReady = false;
    Serial.println("Wi-Fi is not connected");
  }


  // Ultrasonic sensor reading
  ultrasonic_tank_sensor();

  
  //Requests at server GET
  // Serial.println(elapsedTime);
  if (((startTime - elapsedTime) >= 2000) && (objectReady)){
    request_server_get(path_name_irrigation, irrigationdata);
    
    request_server_post(path_name_body, waterdata);
    elapsedTime = startTime;
  }
}



void wifi_connect(){

  digitalWrite(LED_BUILTIN, HIGH);

  //reset settings - for testing
  wm.resetSettings();

  // set configportal timeout
  wm.setConfigPortalTimeout(timeout);

  res = wm.autoConnect("ESP32_WifiConfig","jijijaja");
  if (!res) {
    Serial.println("Failed to connect");
    digitalWrite(LED_BUILTIN, LOW);
    ESP.restart();
  }

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  } 

  Serial.println("");
  Serial.println("WiFi connected...yeey :3");
  digitalWrite(LED_BUILTIN, LOW);
}


void ultrasonic_tank_sensor(){
  
  digitalWrite(trigPin, LOW);  
	delayMicroseconds(2);  
	digitalWrite(trigPin, HIGH);  
	delayMicroseconds(10);  
	digitalWrite(trigPin, LOW);  

  duration = pulseIn(echoPin, HIGH);
  longitude = (duration*.0343)/2;
  Serial.print("Distance: ");
  Serial.println(longitude);
  delay(100);

  return ;

}


void request_server_get(String path_name, JsonDocument doc){
  http.begin(host_name + path_name); //Inicia comunicación HTTP

  int httpCode = http.GET();

  if (!(http.connected())) {
    http.end();
    return;
  }
  
  DeserializationError error;

  // httpCode will be negative on error
  if (httpCode > 0) {
    // file found at server
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      Serial.println(payload);
      error = deserializeJson(doc, payload);
    } else {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] GET... code: %d\n", httpCode);
    }
  } else {
    Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    http.end();
    return;
  }

  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    http.end();
    return;
  }
  Serial.println(waterdata[0]["id"].as<int>());
  http.end();
}


void request_server_post(String path_name, JsonDocument doc){
  http.begin(host_name + path_name); //Inicia comunicación HTTP

  if (!(http.connected())) {
    http.end();
    return;
  }

  String output;


  serializeJsonPretty(doc, output);

  Serial.println(output);

  // int httpCode = http.PUT(String output);

  // // httpCode will be negative on error
  // if (httpCode > 0) {
  //   // file found at server
  //   if (httpCode == HTTP_CODE_OK) {
  //     String payload = http.getString();
  //     Serial.println(payload);

  //   } else {
  //     // HTTP header has been send and Server response header has been handled
  //     Serial.printf("[HTTP] GET... code: %d\n", httpCode);
  //   }
  // } else {
  //   Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
  //   http.end();
  //   return;
  // }

  http.end();
}
