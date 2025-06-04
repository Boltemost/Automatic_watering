
/**
 * OnDemandConfigPortal.ino
 * example of running the configPortal AP manually, independantly from the captiveportal
 * trigger pin will start a configPortal AP for 120 seconds then turn it off.
 * 
 */
#include <bits/stdc++.h>
#include <WiFiManager.h> // https://github.com/tzapu/WiFiManager
#include <WiFi.h>

using namespace std;


//Declaración de variables
const int trigPin = 16;
const int echoPin = 17;
const int TRIGGER_PIN = 120;

float duration, distance; 

int timeout = 10; // seconds to run for

bool res;


void setup() {
  //Inicio de protocolos de comunicación  
  WiFi.mode(WIFI_STA); // explicitly set mode, esp defaults to STA+AP 
  
  Serial.begin(9600); //Inicia comunicación serial
  Serial.println("\n Starting");


  //Asignación de pines
  pinMode(trigPin, OUTPUT);  
	pinMode(echoPin, INPUT);  
  
  pinMode(TRIGGER_PIN, INPUT_PULLUP);


  
}


void loop() { // put your main code here, to run repeatedly:
  // Wifi configuration, triggered by pin 10
  if ( digitalRead(TRIGGER_PIN) == LOW ) {
    thread t(wifi_connect);
    
  }


  // Ultrasonic sensor reading
  digitalWrite(trigPin, LOW);  
	delayMicroseconds(2);  
	digitalWrite(trigPin, HIGH);  
	delayMicroseconds(10);  
	digitalWrite(trigPin, LOW);  

  duration = pulseIn(echoPin, HIGH);
  distance = (duration*.0343)/2;
  Serial.print("Distance: ");
  Serial.println(distance);
  delay(100);

}

void wifi_connect(){
  //Configuración del gestor de WiFi con WifiManager
  WiFiManager wm;

  //reset settings - for testing
  wm.resetSettings();

  // set configportal timeout
  wm.setConfigPortalTimeout(timeout);

  res = wm.autoConnect("ESP32_WifiConfig","jijijaja");
  if (!res){
    Serial.println("Failed to connect");
    ESP.restart();
    delay(5000);
  }

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  } 

  Serial.println("");
  Serial.println("WiFi connected...yeey :3");
}

