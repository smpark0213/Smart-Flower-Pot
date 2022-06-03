/**
 * Smart Flowerpot - Flowerpot Sensing Module
 * Made by Minjae Seon (ddol0225@gmail.com)
 * 2022-1 Gachon Univ., Dept. of Software Embedded System Term Project
 */
#include <ESP8266WiFi.h>
#include <Wire.h>
#include <BH1750.h>
#include <PubSubClient.h>

#define MSG_BUFFER_SIZE (128)
#define PUBLISH_INTERVAL 5000
#define TOPIC_NAME "flowerpot1"

// Wi-Fi Connection Infomation
const char* ssid = "GC_free_WiFi";
const char* pwd = "";
WiFiClient espClient;
unsigned long lastWiFiCheck = 0;

// Mqtt
const char* mqttServer = "172.16.239.43";
const int mqttPort = 1883;
const char* mqttClientName = "SmartFlowerpot1";
unsigned long lastSendTime = 0;
char msg[MSG_BUFFER_SIZE];
PubSubClient mqttClient(espClient);

// Moisture Sensor
const int moisturePin = A0;
int moistureValue = 0;

// Light Sensor
BH1750 lightMeter;
float lightValue = 0.0;

void setup() {
  // Initializing
  Serial.begin(9600);
  Wire.begin();
  
  // Print 
  Serial.println();
  Serial.println("--------- Smart Flowerpot System ---------");
  Serial.println("Made by Team 1");
  Serial.println("System Initiallizing...");

  // Lightmeter
  lightMeter.begin();

  // Connect to WiFi
  Wifi_connect();

  // Connect to MQTT Server
  mqtt_setup();
}

void loop() {
  // Wi-Fi Retry
  if(WiFi.status() != WL_CONNECTED) {
    Serial.println("[Wi-Fi] Disconnected!");
    Wifi_connect();
  }

  // MQTT Retry
  if(!mqttClient.connected()) {
    mqtt_reconnect();
  }

  mqtt_publish();
}

/** Wi-Fi **/
void Wifi_connect() {
    Serial.print("[Wi-Fi] Connected to ");
    Serial.print(ssid);

    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, pwd);
    WiFi.setSleepMode(WIFI_NONE_SLEEP);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }

    Serial.println();
    Serial.println("[Wi-Fi] Wi-Fi Connected!");
    Serial.print("[Wi-Fi] IP : ");
    Serial.println(WiFi.localIP());
}

/** MQTT **/
void mqtt_setup() {
  mqttClient.setServer(mqttServer, mqttPort);
  mqttClient.setCallback(mqtt_callback);
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("[MQTT] Message Arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char) payload[i]);
  }
  Serial.println();
}

void mqtt_reconnect() {
  Serial.print("[MQTT] Connect to ");
  Serial.print(mqttServer);
  while(!mqttClient.connected()) {
    if (mqttClient.connect(mqttClientName)) {
      Serial.println();
      Serial.println("[MQTT] Connected!");
    }
    else {
      Serial.print(".");
    }
    delay(1000);
  }
}

void mqtt_publish() {
  mqttClient.loop();
  
  unsigned long now = millis();
  if (lastSendTime = 0 || now - lastSendTime > PUBLISH_INTERVAL) {
    lastSendTime = now;
    
    // Light
    lightValue = lightMeter.readLightLevel();
    
    // Moisture
    // 0 ~ 300 Dry / 300 ~ 700 Humid / 700~950 In Water
    moistureValue = analogRead(moisturePin);
    
    snprintf(msg, MSG_BUFFER_SIZE, "Moisture %ld / Light %f", moistureValue, lightValue);
    Serial.print("[MQTT] Publish Message : ");
    Serial.println(msg);
    mqttClient.publish(TOPIC_NAME, msg);
  }
  delay(500);
}
