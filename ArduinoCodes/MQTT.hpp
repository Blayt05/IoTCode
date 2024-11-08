
const char* MQTT_BROKER_ADRESS = "10.22.181.132";
const uint16_t MQTT_PORT = 1883;
const char* MQTT_CLIENT_NAME = "ESP8266Client_1";

WiFiClient espClient;
PubSubClient mqttClient(espClient);

void SuscribeMqtt()
{
	mqttClient.subscribe("arduino_1/sensor_deteccion");
}

String payload;
void PublisMqtt(unsigned long data)
{
	payload = "";
	payload = String(data);
	mqttClient.publish("arduino_1/sensor_deteccion", (char*)payload.c_str());
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
	Serial.print(content);
	Serial.println();
}