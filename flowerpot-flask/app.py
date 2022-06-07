from distutils.util import run_2to3
from pydoc import cli
import time
from gpiozero import Motor
import cv2
from pytesseract import image_to_string
import pytesseract
from PIL import Image
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time 

GPIO.setmode(GPIO.BCM)
trig = 2
echo = 3
led_ctrl = 4
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)
GPIO.setup(led_ctrl, GPIO.OUT)

broker_ip = '127.0.0.1'
mqtt_port = 1883
topic = ['flowerpot1', 'flowerpot2']
flowerpot_data = [{'name': 'flowerpot1', 'moisture' : -1, 'light' : -1}, {'name':'flowerpot2', 'moisture' : -1, 'light' : -1}]

# 현재 화분
# 0(forward): flowerpot1, 1(backward): flowerpot2
curr_plant = 0

### OCR ###
cap = cv2.VideoCapture(-1)

def check_distance():
    try :
        while True:
            GPIO.output(trig, False)
            time.sleep(0.5)

            GPIO.output(trig, True)
            time.sleep(0.00001)
            GPIO.output(trig, False)


            while GPIO.input(echo) == 0 :
                pulse_start = time.time()

            while GPIO.input(echo) == 1 :
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17000
            distance = round(distance, 2)
            
            if distance <= 15.0:
                print('detected')
    finally:
        GPIO.cleanup()

### mqtt-python ###
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect ok!")
    else:
        print("Bad connection returned code = ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnectd! rc = " + str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscritbe " + str(mid) + " " +str(granted_qos))

def on_message(client, userdata, msg):
    print(str(msg.payload.decode("utf-8")))
    list= msg.payload.decode().split()
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
    moisture_threshold = 300 
    light_threshold = 1000

    moisutre_trigger = -1
    light_trigger = -1

    # 0,  수분 체크
    if flowerpot_data[0]['moisture'] < moisture_threshold:
        moisutre_trigger = 0
        if curr_plant != moisutre_trigger:
            move()
        watering()
        curr_plant = moisutre_trigger

    # 1,  수분 체크
    if flowerpot_data[1]['moisture'] < moisture_threshold:
        moisutre_trigger = 1
        if curr_plant != moisutre_trigger:
            move()
        watering()
        curr_plant = moisutre_trigger

    # 0,  조도 low 체크
        if flowerpot_data[0]['light'] < light_threshold:
            light_trigger = 0
            if curr_plant != light_trigger:
                move()
            light_on()
            curr_plant = light_trigger

    # 1,  조도 low 체크
    if flowerpot_data[1]['light'] < light_threshold:
        light_trigger = 1
        if curr_plant != light_trigger:
            move()
        light_on()
        curr_plant = light_trigger

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


def watering(speed=1):
    # 워터펌프 : motor5
    motor = Motor(forward=26, backward=21)
    motor.forward(speed)
    time.sleep(2.5)
    motor.stop()


def light_on():
    print('on')
    GPIO.output(led_ctrl, True)
    time.sleep(2)
    print('off')
    GPIO.output(led_ctrl, False)
    time.sleep(2)
    GPIO.cleanup()

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
        for motor in motors:
            motor.forward()
        time.sleep()
        for motor in motors:
            motor.backward()

    # flowerpot1 -> flowerpot2
    if curr_plant == 1:
        for motor in motors:
            motor.backward()
        time.sleep()
        for motor in motors:
            motor.forward()

if __name__ == '__main__':
    print("Flower-Pot-Server Runing...")
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    # run_video = threading.Thread(target=run_video, args=(queueList, errorDict))
    # run_video.start()
    # run_video.join()

    client.connect(broker_ip, mqtt_port)
    client.subscribe(topic[0])
    client.subscribe(topic[1])

    client.loop_forever()

# 앞 화분 (flowerpot1)
def is_plant1(text):
    plant1 = 'plantA'
    input_char = text
    if(plant1 in input_char):
        return 1
    else:
        return 0

# 뒤 화분(flowerpot2)
def is_plant2(text):
    plant1 = 'plantA'
    input_char = text
    if(plant1 in input_char):
        return 1
    else:
        return 0

def video_detector():
    if cap.isOpened():
        while True:
            ret, video = cap.read()
            video = cv2.flip(video, 0)  # 좌우반전
            video = cv2.flip(video, 1)  # 상하반전
            if ret:
                video = cv2.resize(video, dsize=(400, 300), interpolation=cv2.INTER_AREA)

                gray = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, dsize=(400, 300), interpolation=cv2.INTER_AREA)

                threshold = cv2.threshold(gray, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                img_result = cv2.resize(threshold, dsize=(400, 300), interpolation=cv2.INTER_AREA)

                img_result = cv2.medianBlur(img_result, ksize=5)
                text = image_to_string(img_result, lang='eng', config='--psm 1 -c preserve_interword_spaces=1') # Array
                text = text.upper()
                textArr = text.split('\n')
                # print(textArr)

                print("Text = " + str(textArr))

                if cv2.waitKey(1) != -1:
                    break
            else:
                print("no frame")
                break
    else:
        print("can't open camera")


def run_video(queue, errorDict):
    try:
        video_detector()

        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        errorDict['isError'] = True
        print('Error!', e)