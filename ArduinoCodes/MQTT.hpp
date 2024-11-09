
const char* MQTT_BROKER_ADRESS = "10.22.181.132";
const uint16_t MQTT_PORT = 1883;
const char* MQTT_CLIENT_NAME = "ESP8266Client_1";

WiFiClient espClient;
PubSubClient mqttClient(espClient);

// Función para suscribirse a los temas MQTT
void SuscribeMqtt()
{
	mqttClient.subscribe("arduino_1/sensor_deteccion"); // Suscribirse al tema para la deteccion del carro
  mqttClient.subscribe("arduino_1/led_state");  // Suscribirse al tema para el estado de los LEDs
}

// Función para publicar los datos de detección de carro
String payload;
void PublisMqtt(unsigned long data)
{
  payload = "";
  payload = String(data);

  // Publicar los datos en el tópico MQTT
  mqttClient.publish("arduino_1/sensor_deteccion", (char*)payload.c_str());

  // Mostrar los datos en el monitor serial
  Serial.print("Publicando: ");
  Serial.println(payload);
}


// Función para publicar el color del LED y el tiempo en segundos
void PublisMqttLedState(const String& ledColor, int timeOn)
{
    // Crear el payload solo con el color del LED y el tiempo
    String payload = "Color: " + ledColor + ", Tiempo: " + String(timeOn) + " segundos";
    mqttClient.publish("arduino_1/led_state", payload.c_str());  // Publicar en el tema "arduino_1/led_state"
    Serial.println("Publicado: " + payload);  // Para depuración en el monitor serie
}



String content = "";
void OnMqttReceived(char* topic, byte* payload, unsigned int length) 
{
	Serial.print("Received on ");
	Serial.print(topic);
	Serial.print(": ");

	content = "";	
	for (size_t i = 0; i < length; i++) {
		content.concat((char)payload[i]);
	}
	Serial.println(content);
}