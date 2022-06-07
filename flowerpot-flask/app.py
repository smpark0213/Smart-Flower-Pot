from distutils.util import run_2to3
import threading
import multiprocessing
import time
from multiprocessing import Process
from multiprocessing.dummy import Process
from gpiozero import Motor
from flask_socketio import SocketIO
import cv2
from pytesseract import image_to_string
import pytesseract
from PIL import Image
import paho.mqtt.client as mqtt

# mqtt_server
# camera_server
# motor_server

broker_ip = '127.0.0.1'
mqtt_port = 1883
# app = Flask(__name__)

# app.config['MQTT_BROKER_URL'] = broker_ip
# app.config['MQTT_BROKER_PORT'] = mqtt_port
# app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
# socketio = SocketIO(app)
# mqtt = Mqtt(app)

topic = ['flowerpot1', 'flowerpot2', 'flowerpot3']
flowerpot_data = [{'name': 'flowerpot1', 'moisture' : -1, 'light' : -1}, {'name':'flowerpot2', 'moisture' : -1, 'light' : -1}, {'name':'flowerpot3', 'moisture' : -1, 'light' : -1}]
queueList = []
errorDict = {'isError': False}
# 현재 화분
curr_plant = None

### OCR ###
cap = cv2.VideoCapture(-1)

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


### mqtt-python ###
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect ok!")
    else:
        print("Bad connection returned code = ", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_subscribe(client, userdata, mid, granted_qos):
    print("subscritbe " + str(mid) + " " +str(granted_qos))

def on_message(client, userdata, msg):
    print(str(msg.payload.decode("utf-8")))
    list=message.payload.decode().split()
    global flowerpot_data
    # Moisture <int> / Light <float>
    # 0         1   2   3       4
    moisture = float(list[1])
    light = float(list[4])
    update_flower_pots(message.topic, moisture, light)
    # check flower pot

# flowerpot1 == 앞쪽
# flowerpot2 == 뒤쪽

def update_flower_pots(inputTopic, moisture, light):
    global flowerpot_data
    global topic
    print(inputTopic)
    if(inputTopic == topic[0]):
        flowerpot_data[0]['moisture'] = moisture
        flowerpot_data[0]['light'] = light
    elif(inputTopic == topic[1]):
        flowerpot_data[1]['moisture'] = moisture
        flowerpot_data[1]['light'] = light
    elif(inputTopic == topic[2]):
        flowerpot_data[2]['moisture'] = moisture
        flowerpot_data[2]['light'] = light
    else:
        return 0
    print(flowerpot_data)


def check_flowerpot():
    # moisture validation
    # light validation
    return 0


def motor5():
    # 워터펌프 : motor5
    motor5 = Motor(forward=26, backward=21)
    motor5.forward(1)
    time.sleep(2.5)
    motor5.stop()

def run_snesor(queue, errorDict):
    # 바퀴 : motor1 ~ motor4
    motor1 = Motor(forward=17, backward=27)
    motor2 = Motor(forward=22, backward=23)
    motor3 = Motor(forward=5, backward=6)
    motor4 = Motor(forward=13, backward=19)

    # # 워터펌프 : motor5
    # motor5 = Motor(forward=26)
    # motor5.forward(0.5)
    # time.sleep(5)
    # motor5.stop()
    try : 
        while True:
            if queue:
                # 일반 명령어 파싱
                cmd = list(map(int, queue.pop(0).split(';')))
                print(cmd)

                if cmd[0] == 1:
                    try:
                        print('High')
                        motor1.forward()
                        motor2.forward()
                        motor3.forward()
                        motor4.forward()
                        time.sleep(5)
                    finally:
                        motor1.stop()
                        motor2.stop()   
                        motor3.stop()
                        motor4.stop()
                        queue[:] = []
                    

                if cmd[0] == 2:
                    try:
                        print('LOW')
                        motor1.backward()
                        motor2.backward()
                        motor3.backward()
                        motor4.backward()
                        time.sleep(5)
                    finally:
                        motor1.stop()
                        motor2.stop()   
                        motor3.stop()
                        motor4.stop()
                        queue[:] = []
                    
    
    except Exception as e:
        errorDict['isError'] = True
        print('Error!', e)


if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    print("Flower-Pot-Server Runing...")
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    client.connect(broker_ip, mqtt_port)
    for t in topic :
            client.subscribe(t)
    client.loop_forever()

    motor5()

    # 명령 Queue
    queueList
    # Error Check용 Dict
    errorDict

    run_snesor = threading.Thread(target=run_snesor, args=(queueList, errorDict))
    run_video = threading.Thread(target=run_video, args=(queueList, errorDict))

    run_video.start()
    run_snesor.start()

    run_video.join()
    run_snesor.join()