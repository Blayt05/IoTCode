#include <ESP8266WiFi.h>
#include <PubSubClient.h>

#include "config.h"  // Sustituir con datos de vuestra red
#include "MQTT.hpp"
#include "ESP8266_Utils.hpp"
#include "ESP8266_Utils_MQTT.hpp"

// Definimos los pines para el sensor ultrasónico y los LEDs
const int trigPin = 12;
const int echoPin = 14;
  // const int ledVerde = 5;
  // const int ledAmarillo = 4;
  // const int ledRojo = 0;


void setup(void)
{

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
 

	Serial.begin(115200);
	SPIFFS.begin();

	ConnectWiFi_STA(false);

	InitMqtt();
}


void loop()
{

  int deteccion = detectarCarro(); //Llama a detectarCarro y guarda el resultado
  PublisMqtt(deteccion); // Lo que hace es llamar a una funcion que publica el dato "1" o "0"
  delay(1000);
  
	HandleMqtt();

	

	delay(1000);
}


//Funcion para detectar si hay un carro y mandar cierto dato
int detectarCarro() {
  long duracion, distancia;

  //Enviar los pulsos a trig
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Leer la duración del pulso en el ECHO
  duracion = pulseIn(echoPin, HIGH);

   // Calcular distancia en cm
  distancia = duracion * 0.034 / 2;

  // Calcular si la distancia es menor a 30 cm 
  if (distancia < 30 && distancia > 0) {
        // Si se detecta un carro a menos de 30 cm
        Serial.println("Carro detectado");
        return 1;  // Retorna 1 si detecta un carro
    } else {
        // Si no se detecta un carro en ese rango
        Serial.println("No se detecto carro");
        return 0;  // Retorna 0 si no detecta nada
    }

}




