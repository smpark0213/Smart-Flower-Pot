const Gpio = require('pigpio').Gpio;
const gpio = require('./configs/gpio');
const mqtt = require('./configs/mqtt');
const firebase = require('./configs/firebase');
const microtime = require("microtime");
const { sleep, check_move_direction } = require('./configs/utils');

/** Variables **/

// Threshold
const moisture_threshold = 300
const light_threshold = 500
const ocrtime_threshold = 10000

// 물 줄 주기
const water_time = 43200000;

// 태양빛 주기
const light_time = 3600000;

// 체크 주기
const check_time = 300000;

// 마지막 물 준 시간
const water_lasttime = [0, 0, 0];

// 마지막 태양 시간
const light_lasttime = [0, 0, 0];

// 마지막 OCR 요청 시간
let ocr_lasttime = -1;

// 현재 식물
let curr_plant = -1;

// 마지막 명령의 대상 식물 (-1 : 없음)
let lastWantedPlant = -1;

// 마지막 명령 (-1 : 없음, 0: 물주기, 1: LED 켜기)
let lastCommand = -1;

// 마지막 명령 완료 여부
let isLastCmdFinished = true;

// 움직이고 있는 여부
let isMoving = false;

// MQTT
const mqtt_topic = ['flowerpot1', 'flowerpot2', 'flowerpot3', 'plantdetect'];
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

    if (mqtt_client.connected) {
        // MQTT Subscribed
        mqtt_client.subscribe(mqtt_topic, { qos: 1 });
    }
    else {
        process.exit(-1);
    }
};

const mqtt_on_message = async (topic, message, packet) => {
    //console.log(`[MQTT/${topic}] Message Received : ${message}`);
    const msg = message.toString();
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
    }

    if (topic === "plantdetect") {
        if (msg === 'planta')
            curr_plant = 0;
        else if (msg === 'plantb')
            curr_plant = 1;
        else if (msg === 'plantc')
            curr_plant = 2;

        console.log("detected: ", msg);
        await detect_callback();
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

async function check_status() {
    console.log("Start Check Status")
    console.log(flowerpot_data);

    const current_time = microtime.nowDouble();
    const moisture = [0, 0, 0]
    const light = [0, 0, 0]

    // plant A
    if (flowerpot_data[0]['moisture'] !== -1 || flowerpot_data[0]['light'] !== -1) {
        moisture[0] = flowerpot_data[0]['moisture'];
        light[0] = flowerpot_data[0]['light'];

        if (moisture[0] < moisture_threshold) {
            if (current_time - water_lasttime[0] >= water_time) {
                console.log('Plant 0 Water');
                if (curr_plant !== 0) {
                    lastWantedPlant = 0;
                    lastCommand = 0;
                    await move(0);
                }
                else if (curr_plant === 0) {
                    water_lasttime[0] = current_time;
                    await run_waterpump();
                }
                return;
            }
        } else if (light[0] < light_threshold) {
            if (current_time - light_lasttime[0] >= light_time) {
                console.log('Plant 0 Light');
                if (curr_plant !== 0) {
                    lastWantedPlant = 0;
                    lastCommand = 1;
                    await move(0);
                }
                else if (curr_plant === 0) {
                    light_lasttime[0] = current_time;
                    await control_light(true);
                }
                return;
            }
        }
    }

    // plant B
    if (flowerpot_data[1]['moisture'] !== -1 || flowerpot_data[1]['light'] !== -1) {
        moisture[1] = flowerpot_data[1]['moisture'];
        light[1] = flowerpot_data[1]['light'];

        if (moisture[1] < moisture_threshold) {
            if (current_time - water_lasttime[1] >= water_time) {
                console.log('Plant 1 Water');
                if (curr_plant !== 1) {
                    lastWantedPlant = 1;
                    lastCommand = 0;
                    await move(1);
                }
                else if (curr_plant === 1) {
                    water_lasttime[1] = current_time;
                    await run_waterpump();
                }
                return;
            }
        } else if (light[1] < light_threshold) {
            if (current_time - light_lasttime[1] >= light_time) {
                console.log('Plant 1 Light');
                if (curr_plant !== 1) {
                    lastWantedPlant = 1;
                    lastCommand = 1;
                    await move(1);
                }
                else if (curr_plant === 1) {
                    light_lasttime[1] = current_time;
                    await control_light(true);
                }
                return;
            }
        }
    }

    // plant C
    if (flowerpot_data[2]['moisture'] !== -1 || flowerpot_data[2]['light'] !== -1) {
        moisture[2] = flowerpot_data[2]['moisture'];
        light[2] = flowerpot_data[2]['light'];

        if (moisture[2] < moisture_threshold) {
            if (current_time - water_lasttime[2] >= water_time) {
                console.log('Plant 2 Water');
                if (curr_plant !== 2) {
                    lastWantedPlant = 2;
                    lastCommand = 0;
                    await move(2);
                }
                else if (curr_plant === 2) {
                    water_lasttime[2] = current_time;
                    await run_waterpump();
                }
                return;
            }
        } else if (light[2] < light_threshold) {
            if (current_time - light_lasttime[2] >= light_time) {
                console.log('Plant 2 Water');
                if (curr_plant !== 2) {
                    lastWantedPlant = 2;
                    lastCommand = 1;
                    await move(2);
                }
                else if (curr_plant === 2) {
                    light_lasttime[2] = current_time;
                    await control_light(true);
                }
                return;
            }
        }
    }

    console.log("All Well - Ignored");
    isLastCmdFinished = true;
}

// 모터
async function move(target_plant) {
    console.log("isMoving", isMoving);

    if (isMoving)
        return;

    isMoving = true;
    control_light(false)
    const direction = check_move_direction(curr_plant, target_plant);

    if (direction === -1) {
        gpio.runMotor(motor1Forward, motor1Pwm, 60);
        gpio.runMotor(motor2Forward, motor2Pwm, 60);
    } else if (direction === 1) {
        gpio.runMotor(motor1Backward, motor1Pwm, 60);
        gpio.runMotor(motor2Backward, motor2Pwm, 60);
    } else if (direction === 0) {
        isMoving = false;
        return;
    }


    await sleep(1000);

    await gpio.checkDistanceByUltrasonic(trig, echo, 9.5, async function () {
        // 모터 정지
        stop_motor();
        isMoving = false;

        // OCR 판독 요청
        setTimeout(function () {
            mqtt_client.publish('ocrrequest', 'true', { qos: 2 })
            ocr_lasttime = microtime.nowDouble();
        });
    });
}

async function detect_callback() {
    console.log(`lastWanted ${lastWantedPlant} / Current ${curr_plant} / Last Cmd ${lastCommand}`);
    if (lastWantedPlant !== -1 && lastWantedPlant === curr_plant) {
        const current_time = microtime.nowDouble();
        // 물 
        if (lastCommand === 0) {
            water_lasttime[lastWantedPlant] = current_time;
            run_waterpump();
        }
        // 불
        else if (lastCommand === 1) {
            light_lasttime[lastWantedPlant] = current_time;
            control_light(true);
        }

        lastWantedPlant = -1;
        lastCommand = -1;
        isLastCmdFinished = true;
    }
    else {
        move(lastWantedPlant);
    }
}

// 워터펌프
async function run_waterpump() {
    console.log('run water motor');
    gpio.runMotor(waterMotor, waterMotorPwm, 60);

    console.log('sleep water motor')
    await sleep(2000);

    console.log('stop water motor')
    gpio.stopMotor(waterMotor, waterMotorPwm);
}

// LED 제어
async function control_light(isOn) {
    if (isOn) {
        gpio.sendLow(ledControl);
    }
    else {
        gpio.sendHigh(ledControl);
    }
}

async function stop_motor() {
    gpio.stopMotor(motor1Forward, motor1Pwm);
    gpio.stopMotor(motor2Forward, motor2Pwm);
    gpio.stopMotor(motor1Backward, motor1Pwm);
    gpio.stopMotor(motor2Backward, motor2Pwm);
    isMoving = false;
}

async function stop_waterpump() {
    gpio.stopMotor(waterMotor, waterMotorPwm);
}

// Ctrl + C 동작
process.on('SIGINT', async function () {
    // 모든 모터 멈추기
    stop_motor();
    stop_waterpump();

    // 라이트 끄기
    control_light(false);

    process.exit(2);
});

// 5분 간격으로 조도 / 습도 확인
setInterval(async function () {
    console.log(`cmd last finished : ${isLastCmdFinished} / ismoving : ${isMoving}`);

    // 마지막 명령이 처리가 끝났으며, 움직이는 상태가 아닌 경우
    if (isLastCmdFinished && !isMoving) {
        // 상태 확인 시작
        isLastCmdFinished = false;
        check_status();
    }
    else {
        console.log("not finished - ismoving");
    }
}, 30000);

// 5분 간격으로 Firebase Update
setInterval(async () => {
    await firebase.updateFirebaseFlowerPot(flowerpot_data);
}, check_time);