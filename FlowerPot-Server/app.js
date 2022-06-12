const Gpio = require('pigpio').Gpio;
const gpio = require('./configs/gpio');
const mqtt = require('./configs/mqtt');

/** Variables **/
// MQTT
const mqtt_topic = ['flowerpot1', 'flowerpot2'];
const flowerpot_data = [
    {'name': 'flowerpot1', 'moisture': -1, 'light': -1},
    {'name': 'flowerpot2', 'moisture': -1, 'light': -1}
];
const mqtt_error = (error) => {
    console.error("[MQTT] Connection Error", error);
};
const mqtt_connect = () => {
    console.log(`[MQTT] Connecting to ${mqtt_client.options.hostname}:${mqtt_client.options.port} / isSuccess : ${mqtt_client.connected}`);
};
const mqtt_on_message = (topic, message, packet) => {
    const msg_list = message.toString().split(' ');

    if (topic === 'flowerpot1') {
        flowerpot_data[0]['moisture'] = Number(msg_list[1]);
        flowerpot_data[0]['light'] = Number(msg_list[4]);
    }
    else if (topic === 'flowerpot2') {
        flowerpot_data[1]['moisture'] = Number(msg_list[1]);
        flowerpot_data[1]['light'] = Number(msg_list[4]);
    }
    console.log(`[MQTT/${topic}] Message Received : ${message}`);
    console.log(flowerpot_data);
};

const mqtt_client = mqtt.connectMqtt();
mqtt_client.on("connect", mqtt_connect);
mqtt_client.on("error", mqtt_error);
mqtt_client.on("message", mqtt_on_message);

// Ultrasonic Pin
const trigPin = 2;
const trig = new Gpio(trigPin, {mode: Gpio.OUTPUT});

const echoPin = 3;
const echo = new Gpio(echoPin, {mode: Gpio.INPUT});

// Led Pin
const ledControlPin = 4;
const ledControl = new Gpio(ledControlPin, {mode: Gpio.OUTPUT});

// Motor Pin
const motor1Pins = [17, 27];
const motor1Forward = new Gpio(motor1Pins[0], {mode: Gpio.OUTPUT});
const motor1Backward = new Gpio(motor1Pins[1], {mode: Gpio.OUTPUT});

const motor2Pins = [22, 23];
const motor2Forward = new Gpio(motor2Pins[0], {mode: Gpio.OUTPUT});
const motor2Backward = new Gpio(motor2Pins[1], {mode: Gpio.OUTPUT});

const motor1PwmPin = 5;
const motor1Pwm = new Gpio(motor1PwmPin, {mode: Gpio.OUTPUT});

const motor2PwmPin = 6;
const motor2Pwm = new Gpio(motor2PwmPin, {mode: Gpio.OUTPUT});

function main() {
    // MQTT Subscribed
    mqtt_client.subscribe(mqtt_topic, {qos: 1});

    // Test
    setTimeout(function () {
        gpio.runMotor(motor1Forward, motor1Pwm, 127);
        gpio.runMotor(motor2Forward, motor2Pwm, 127);
    }, 3000);

    setTimeout(function () {
        gpio.stopMotor(motor1Forward, motor1Pwm);
        gpio.stopMotor(motor2Forward, motor2Pwm);
    }, 6000);
}

main();