const { sleep } = require("./utils");
const microtime = require("microtime");

const HIGH = 1;
const LOW = 0;

/**
 * 모터 제어
 * @param motorGpio Motor Gpio
 * @param pwmGpio Motor PWM Control Gpio
 * @param pwmValue PWM Value
 * @return {boolean}
 */
async function runMotor(motorGpio, pwmGpio, pwmValue) {
    console.log('run');
    try {
        if (0 < pwmValue && pwmValue <= 255) {
            await motorGpio.digitalWrite(HIGH);
            await pwmGpio.pwmWrite(pwmValue)
            return true;
        }
        else {
            return false;
        }
    }
    catch (e) {
        console.error("Error!", e);
        return false;
    }
}

/**
 * 모터 정지
 * @param motorGpio Motor Gpio
 * @param pwmGpio Motor PWM Control Gpio
 * @return {boolean}
 */
async function stopMotor(motorGpio, pwmGpio) {
    try {
        await motorGpio.digitalWrite(LOW);
        await pwmGpio.pwmWrite(0)
        return true;
    }
    catch (e) {
        console.error("Error!", e);
        return false;
    }
}

/**
 * HIGH 보내기
 * @param gpio
 * @return {boolean}
 */
async function sendHigh(gpio) {
    try {
        gpio.digitalWrite(HIGH);
        return true;
    }
    catch (e) {
        console.error("Error!", e);
        return false;
    }
}

/**
 * LOW 보내기
 * @param gpio
 * @return {boolean}
 */
async function sendLow(gpio) {
    try {
        gpio.digitalWrite(LOW);
        return true;
    }
    catch (e) {
        console.error("Error!", e);
        return false;
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
        await sleep(500);

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