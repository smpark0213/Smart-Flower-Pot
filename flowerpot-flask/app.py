from distutils.util import run_2to3
from pydoc import cli
from socketserver import ThreadingUDPServer
import time
from gpiozero import Motor
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

trig = 2
echo = 3
led_ctrl = 4

broker_ip = '127.0.0.1'
mqtt_port = 1883
topic = ['flowerpot1', 'flowerpot2']
flowerpot_data = [{'name': 'flowerpot1', 'moisture': -1, 'light': -1},
                  {'name': 'flowerpot2', 'moisture': -1, 'light': -1}]
led_enable = False
water_time = 43200000
last_time = [0, 0]

# 현재 화분
# 0(forward): flowerpot1, 1(backward): flowerpot2
curr_plant = 0


def check_distance():
    try:
        while True:
            GPIO.output(trig, False)
            time.sleep(0.5)

            GPIO.output(trig, True)
            time.sleep(0.00001)
            GPIO.output(trig, False)

            while GPIO.input(echo) == 0:
                pulse_start = time.time()

            while GPIO.input(echo) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17000
            distance = round(distance, 2)

            if distance <= 15.0:
                print('detected')
                break
    finally:
        pass
        # GPIO.cleanup()

### mqtt-python ###


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect ok!")
    else:
        print("Bad connection returned code = ", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnectd! rc = " + str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscritbe " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    print(str(msg.payload.decode("utf-8")))
    list = msg.payload.decode().split()
    global flowerpot_data
    # Moisture <int> / Light <float>
    # 0         1   2   3       4
    moisture = float(list[1])
    light = float(list[4])
    # update flower pots
    update_flower_pots(msg.topic, moisture, light)
    # check flower pots
    check_flower_pots()

# flowerpot1 == 앞쪽
# flowerpot2 == 뒤쪽


def check_flower_pots():
    global flowerpot_data
    global curr_plant
    global moisutre_trigger
    global light_trigger
    global last_time

    print(last_time)

    moisture_threshold = 700
    light_threshold = 100

    print('current:', moisutre_trigger, light_trigger)

    if flowerpot_data[0]['moisture'] == -1 or flowerpot_data[1]['moisture'] == -1 or flowerpot_data[0]['light'] == -1 or flowerpot_data[1]['light'] == -1:
        return

    if (int(round(time.time() * 1000)) - last_time[0]) >= water_time and flowerpot_data[0]['moisture'] < moisture_threshold:
        if curr_plant == 0 and (moisutre_trigger == -1 or moisutre_trigger == 0):
            time_cal = int(round(time.time() * 1000)) - last_time[0]
            print('mois0', time_cal)
            if time_cal >= water_time:
                watering()
                moisutre_trigger = 0
                curr_plant = 0
                last_time[0] = int(round(time.time() * 1000))
        else:
            move()
            watering()
            moisutre_trigger = 0
            curr_plant = 0
            last_time[0] = int(round(time.time() * 1000))

    if flowerpot_data[0]['light'] < light_threshold:
        if curr_plant == 0:
            light_on()
            light_trigger = 0
            curr_plant = 0
        else:
            light_off()
            move()
            light_on()
            light_trigger = 0
            curr_plant = 0

    if (int(round(time.time() * 1000)) - last_time[1]) >= water_time and flowerpot_data[1]['moisture'] < moisture_threshold:
        if curr_plant == 1 and (moisutre_trigger == 1):
            print('mois1', time_cal)
            if time_cal >= water_time:
                watering()
                moisutre_trigger = 1
                curr_plant = 1
                last_time[1] = int(round(time.time() * 1000))
        else:
            move()
            watering()
            moisutre_trigger = 1
            curr_plant = 1
            last_time[1] = int(round(time.time() * 1000))

    if flowerpot_data[1]['light'] < light_threshold:
        if curr_plant == 1:
            light_on()
            light_trigger = 1
            curr_plant = 1
        else:
            light_off()
            move()
            light_on()
            light_trigger = 1
            curr_plant = 1


def update_flower_pots(inputTopic, moisture, light):
    global flowerpot_data
    global topic
    if(inputTopic == topic[0]):
        flowerpot_data[0]['moisture'] = moisture
        flowerpot_data[0]['light'] = light
    elif(inputTopic == topic[1]):
        flowerpot_data[1]['moisture'] = moisture
        flowerpot_data[1]['light'] = light
    else:
        print("update flowerpots error")
        return 0
    print(flowerpot_data)


def watering(speed=1.0):
    # 워터펌프 : motor5
    print("watering start")
    motor = Motor(forward=16, backward=21)
    motor.forward(speed)
    time.sleep(2)
    motor.stop()
    print("watering stop")


def light_on():
    global led_enable
    try:
        if not led_enable:
            print('led on')
            GPIO.output(led_ctrl, False)
            led_enable = True
            time.sleep(2)
    finally:
        pass
        # GPIO.cleanup()


def light_off():
    global led_enable
    try:
        if led_enable:
            print('led off')
            GPIO.output(led_ctrl, True)
            led_enable = False
            time.sleep(2)
    finally:
        pass
        # GPIO.cleanup()


def move():
    global curr_plant
    # 바퀴 : motor1 ~ motor4
    motor1 = Motor(forward=17, backward=27)
    motor2 = Motor(forward=22, backward=23)
    motor3 = Motor(forward=5, backward=6)
    motor4 = Motor(forward=13, backward=19)
    motors = [motor1, motor2, motor3, motor4]
    # flowerpot1 -> flowerpot2
    if curr_plant == 0:
        print("foward")
        for motor in motors:
            motor.forward(0.1)
        time.sleep(1.5)
        check_distance()
        time.sleep(0.5)
        for motor in motors:
            motor.stop()
        print("stop")

    # flowerpot2 -> flowerpot1
    if curr_plant == 1:
        print("backward")
        for motor in motors:
            motor.backward(0.1)
        time.sleep(1)
        check_distance()
        time.sleep(1)
        for motor in motors:
            motor.stop()
        print("stop")


if __name__ == '__main__':
    global moisutre_trigger
    global light_trigger

    print("Flower-Pot-Server Running...")
    moisutre_trigger = -1
    light_trigger = -1

    client = mqtt.Client()

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trig, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)
    GPIO.setup(led_ctrl, GPIO.OUT)
    GPIO.output(led_ctrl, True)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    client.connect(broker_ip, mqtt_port)
    client.subscribe(topic[0])
    client.subscribe(topic[1])

    client.loop_forever()
