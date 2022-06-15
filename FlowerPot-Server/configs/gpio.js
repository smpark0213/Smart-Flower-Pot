const { sleep } = require("./utils");
const microtime = require("microtime");

const HIGH = 1;
const LOW = 0;

/**
 * 모터 제어
 * @param motorGpio Motor Gpio
 * @param pwmGpio Motor PWM Control Gpio
 * @param pwmValue PWM Value
 * @return {Promise<void>}
 */
async function runMotor(motorGpio, pwmGpio, pwmValue) {
    console.log('run');
    try {
        if (0 < pwmValue && pwmValue <= 255) {
            await motorGpio.pwmWrite(pwmValue);
            await pwmGpio.pwmWrite(pwmValue)
        }
    }
    catch (e) {
        console.error("Error!", e);
    }
}

/**
 * 모터 정지
 * @param motorGpio Motor Gpio
 * @param pwmGpio Motor PWM Control Gpio
 * @return {Promise<void>}
 */
async function stopMotor(motorGpio, pwmGpio) {
    console.log('stop');
    try {
        await motorGpio.digitalWrite(LOW);
        await pwmGpio.pwmWrite(0)
    }
    catch (e) {
        console.error("Error!", e);
    }
}

/**
 * HIGH 보내기
 * @param gpio
 * @return {Promise<void>}
 */
async function sendHigh(gpio) {
    try {
        await gpio.digitalWrite(HIGH);
    }
    catch (e) {
        console.error("Error!", e);
    }
}

/**
 * LOW 보내기
 * @param gpio
 * @return {Promise<void>}
 */
async function sendLow(gpio) {
    try {
        await gpio.digitalWrite(LOW);
    }
    catch (e) {
        console.error("Error!", e);
    }
}

/**
 * 초음파 센서로 거리 체크
 * @param trigGpio Trigger Gpio
 * @param echoGpio Echo Gpio
 * @param distance Float Distance (cm)
 * @param callback Callback Function
 * @return {Promise<void>}
 */
async function checkDistanceByUltrasonic(trigGpio, echoGpio, distance, callback) {
    while (true) {
        let pulse_start = -1;
        let pulse_end = -1;

        trigGpio.digitalWrite(LOW);
        await sleep(300);

        trigGpio.digitalWrite(HIGH);
        await sleep(0.01);
        trigGpio.digitalWrite(LOW);

        while (echoGpio.digitalRead() === LOW)
            pulse_start = microtime.nowDouble();

        while (echoGpio.digitalRead() === HIGH)
            pulse_end = microtime.nowDouble();

        const pulse_duration = pulse_end - pulse_start;
        let pulse_distance = pulse_duration * 17000;
        pulse_distance = parseFloat(pulse_distance.toFixed(2));

        console.log(pulse_distance);
        if (pulse_distance <= distance) {
            callback();
            break
        }
    }
}

module.exports = {
    runMotor,
    stopMotor,
    sendHigh,
    sendLow,
    checkDistanceByUltrasonic
}