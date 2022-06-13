const Gpio = require('pigpio').Gpio;
const gpio = require('./configs/gpio');
const mqtt = require('./configs/mqtt');
const firebase = require('./configs/firebase');
const { sleep, check_move_direction } = require('./configs/utils');

/** Variables **/

// Threshold
const moisture_threshold = 700
const light_threshold = 100

// 물 줄 주기
const water_time = 43200000;

// 태양빛 주기
const light_time = 3600000;

// 마지막 물 준 시간
const water_lasttime = [0, 0, 0];

// 마지막 태양 시간
const light_lasttime = [0, 0, 0];

// 현재 식물
let curr_plant = -1;

// MQTT
const mqtt_topic = ['flowerpot1', 'flowerpot2', 'flowerpot3'];
const flowerpot_data = [
    { 'name': 'flowerpot1', 'moisture': -1, 'light': -1 },
    { 'name': 'flowerpot2', 'moisture': -1, 'light': -1 },
    { 'name': 'flowerpot3', 'moisture': -1, 'light': -1 }
];
const mqtt_error = (error) => {
    console.error("[MQTT] Connection Error", error);
};
const mqtt_connect = () => {
    console.log(`[MQTT] Connecting to ${mqtt_client.options.hostname}:${mqtt_client.options.port} / isSuccess : ${mqtt_client.connected}`);
};
const mqtt_on_message = async (topic, message, packet) => {
    console.log(`[MQTT/${topic}] Message Received : ${message}`);

    // 식물 센서 토픽이 Publish 된 경우
    if (topic.includes('flowerpot')) {
        // 종류에 따라 센서 정보 업데이트
        const msg_list = message.toString().split(' ');
        if (topic === 'flowerpot1') {
            flowerpot_data[0]['moisture'] = Number(msg_list[1]);
            flowerpot_data[0]['light'] = Number(msg_list[4]);
        } else if (topic === 'flowerpot2') {
            flowerpot_data[1]['moisture'] = Number(msg_list[1]);
            flowerpot_data[1]['light'] = Number(msg_list[4]);
        } else if (topic === 'flowerpot3') {
            flowerpot_data[2]['moisture'] = Number(msg_list[1]);
            flowerpot_data[2]['light'] = Number(msg_list[4]);
        }
        console.log(flowerpot_data);

        // 상태 확인
        await check_status();
    }
    // 식물 감지 토픽이 Publish 된 경우
    else if (topic === 'plantdetect') {
        const lowerText = message.toLowerCase();

        if (lowerText.includes('planta')) {
            curr_plant = 0;
        } else if (lowerText.includes('plantb')) {
            curr_plant = 1;
        } else if (lowerText.includes('plantc')) {
            curr_plant = 2;
        }
    }
};

const mqtt_client = mqtt.connectMqtt();
mqtt_client.on("connect", mqtt_connect);
mqtt_client.on("error", mqtt_error);
mqtt_client.on("message", mqtt_on_message);

// Ultrasonic Pin
const trigPin = 2;
const trig = new Gpio(trigPin, { mode: Gpio.OUTPUT });

const echoPin = 3;
const echo = new Gpio(echoPin, { mode: Gpio.INPUT });

// Led Pin
const ledControlPin = 4;
const ledControl = new Gpio(ledControlPin, { mode: Gpio.OUTPUT });

// Motor Pin
const motor1Pins = [17, 27];
const motor1Forward = new Gpio(motor1Pins[0], { mode: Gpio.OUTPUT });
const motor1Backward = new Gpio(motor1Pins[1], { mode: Gpio.OUTPUT });

const motor2Pins = [22, 23];
const motor2Forward = new Gpio(motor2Pins[0], { mode: Gpio.OUTPUT });
const motor2Backward = new Gpio(motor2Pins[1], { mode: Gpio.OUTPUT });

const motor1PwmPin = 5;
const motor1Pwm = new Gpio(motor1PwmPin, { mode: Gpio.OUTPUT });

const motor2PwmPin = 6;
const motor2Pwm = new Gpio(motor2PwmPin, { mode: Gpio.OUTPUT });

const waterMotorPin = 16;
const waterMotor = new Gpio(waterMotorPin, { mode: Gpio.OUTPUT });

const waterMotorPwmPin = 26;
const waterMotorPwm = new Gpio(waterMotorPwmPin, { mode: Gpio.OUTPUT });

function main() {
    // MQTT Subscribed
    mqtt_client.subscribe(mqtt_topic, { qos: 1 });

    // 5분 후 Firebase upate
    setTimeout(() => {
        firebase.updateFirebaseFlowerPot(flowerpot_data);
    }, 1000 * 60 * 5)
}

async function check_status() {
    const current_time = microtime.nowDouble();
    if (flowerpot_data[0]['moisture'] !== -1 || flowerpot_data[0]['light'] !== -1) {
        const moisture0 = flowerpot_data[0]['moisture'];
        const light0 = flowerpot_data[0]['light'];

        if (moisture0 < moisture_threshold) {
            if (current_time - water_lasttime[0] >= water_time) {
                while (curr_plant !== 0) {
                    await move(0);
                }

                water_lasttime[0] = current_time;
                await run_waterpump();
            }
        }

        if (light0 < light_threshold) {
            if (current_time - light_lasttime[0] >= light_time) {
                while (curr_plant !== 0) {
                    await move(0);
                }

                light_lasttime[0] = current_time;
                await control_light(true);
            }
        }
    }

    if (flowerpot_data[1]['moisture'] !== -1 || flowerpot_data[1]['light'] !== -1) {
        const moisture1 = flowerpot_data[1]['moisture'];
        const light1 = flowerpot_data[1]['light'];

        if (moisture1 < moisture_threshold) {
            if (current_time - water_lasttime[1] >= water_time) {
                while (curr_plant !== 1) {
                    await move(1);
                }

                water_lasttime[1] = current_time;
                await run_waterpump();
            }
        }

        if (light1 < light_threshold) {
            if (current_time - light_lasttime[1] >= light_time) {
                while (curr_plant !== 1) {
                    await move(1);
                }

                light_lasttime[1] = current_time;
                await control_light(true);
            }
        }
    }

    if (flowerpot_data[2]['moisture'] !== -1 || flowerpot_data[2]['light'] !== -1) {
        const moisture2 = flowerpot_data[2]['moisture'];
        const light2 = flowerpot_data[2]['light'];

        if (moisture2 < moisture_threshold) {
            if (current_time - water_lasttime[2] >= water_time) {
                while (curr_plant !== 2) {
                    await move(2);
                }

                water_lasttime[1] = current_time;
                await run_waterpump();
            }
        }

        if (light2 < light_threshold) {
            if (current_time - light_lasttime[2] >= light_time) {
                while (curr_plant !== 2) {
                    await move(2);
                }

                light_lasttime[2] = current_time;
                await control_light(true);
            }
        }
    }
}

// 모터
async function move(target_plant) {
    await control_light(false)
    const direction = check_move_direction(curr_plant, target_plant);

    if (direction === 1) {
        await gpio.runMotor(motor1Forward, motor1Pwm, 60);
        await gpio.runMotor(motor2Forward, motor2Pwm, 60);
    }
    else if (direction === -1) {
        await gpio.runMotor(motor1Backward, motor1Pwm, 60);
        await gpio.runMotor(motor2Backward, motor2Pwm, 60);
    }
    else if (direction === 0)
        return;

    await gpio.checkDistanceByUltrasonic(trig, echo, 15.0, callback_motor);
}

// 워터펌프
async function run_waterpump() {
    await gpio.runMotor(waterMotor, waterMotorPwm, 60);
    await sleep(2000);
    await gpio.stopMotor(waterMotor, waterMotorPwm);
}

// 초음파 센서 Callback
async function callback_motor() {
    await gpio.stopMotor(motor1Forward, motor1Pwm);
    await gpio.stopMotor(motor2Forward, motor2Pwm);
    await gpio.stopMotor(motor1Backward, motor1Pwm);
    await gpio.stopMotor(motor2Backward, motor2Pwm);

    // OCR 판독 요청
    mqtt_client.publish('ocrrequest', 'true', { qos: 2 })
}

// LED 제어
async function control_light(isOn) {
    if (isOn) {
        await gpio.sendLow(ledControl);
    }
    else {
        await gpio.sendHigh(ledControl);
    }
}

// Ctrl + C 동작
process.on('SIGINT', async function () {
    // 모든 모터 멈추기
    await gpio.stopMotor(motor1Forward, motor1Pwm);
    await gpio.stopMotor(motor2Forward, motor2Pwm);
    await gpio.stopMotor(motor1Backward, motor1Pwm);
    await gpio.stopMotor(motor2Backward, motor2Pwm);
    process.exit(2);
});

main()