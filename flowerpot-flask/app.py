from distutils.util import run_2to3
import multiprocessing
import time
import eventlet
from multiprocessing import Process
from multiprocessing.dummy import Process
from flask import Flask, jsonify
from flask_mqtt import Mqtt
from gpiozero import Motor
from flask_socketio import SocketIO

#eventlet.monkey_patch()
broker_ip = '127.0.0.1'
mqtt_port = 1883
app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = broker_ip
app.config['MQTT_BROKER_PORT'] = mqtt_port
# app.config['MQTT_USERNAME'] = 'user'
# app.config['MQTT_PASSWORD'] = 'secret'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
socketio = SocketIO(app)
mqtt = Mqtt(app)

topic = ['flowerpot1', 'flowerpot2', 'flowerpot3']
flowerpot_data = [{'flowerpot1': {}}, {'flowerpot2': {}}, {'flowerpot3': {}}]

### flask-mqtt ###
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    global topic
    if(rc == 0):
        for t in topic :
            mqtt.subscribe(t)
    else:
        print("Bad connection Returned code = ", rc)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    list=message.payload.decode().split()
    global flowerpot_data
    # Moisture <int> / Light <float>
    # 0         1   2   3       4
    moisture = float(list[1])
    light = float(list[4])
    update_flower_pots(message.topic, moisture, light)


def update_flower_pots(inputTopic, moisture, light):
    global flowerpot_data
    global topic
    print(inputTopic)
    if(inputTopic == topic[0]):
        flowerpot_data[0][topic[0]]['moisture'] = moisture
        flowerpot_data[0][topic[0]]['light'] = light
    elif(inputTopic == topic[1]):
        flowerpot_data[1][topic[1]]['moisture'] = moisture
        flowerpot_data[1][topic[1]]['light'] = light
    elif(inputTopic == topic[2]):
        flowerpot_data[2][topic[2]]['moisture'] = moisture
        flowerpot_data[2][topic[2]]['light'] = light
    else:
        return 0
    print(flowerpot_data)


def run_snesor(queue, errorDict):
    motor1 = Motor(forward=17, backward=27)
    motor2 = Motor(forward=22, backward=23)
    motor3 = Motor(forward=5, backward=6)
    motor4 = Motor(forward=13, backward=19)

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
                        continue

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
                        continue
    
    except Exception as e:
        errorDict['isError'] = True
        print('Error!', e)


def run_flask(queue, errorDict):
    # flowerpot들의 센서 정보
    @app.route('/flowerpot')
    def get_flowerpot1():
        if not errorDict['isError']:
            global flowerpot_data
            return jsonify(
                code=200, success=True,
                msg = flowerpot_data
            )
        else:
            return jsonify(
                code=500,
                success=False,
                msg='Mqtt Connection Error'
            )

    # 전진
    @app.route('/forward')
    def move_forward():
        if not errorDict['isError']:
            queue.append('1;0')
            return jsonify(
                code=200,
                success=True,
                msg='OK'
            )
        else:
            return jsonify(
                code=500,
                success=False,
                msg='Sensor Connection Error'
            )

    # 후진
    @app.route('/backward')
    def move_backward():
        if not errorDict['isError']:
            queue.append('2;0')
            return jsonify(
                code=200,
                success=True,
                msg='OK'
            )
        else:
            return jsonify(
                code=500,
                success=False,
                msg='Sensor Connection Error'
            )

    # Flask-MQTT only supports running with one instance
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)


if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    print("Flower-Pot-Server Runing...")

    #MultiProcessor간 변수 공유를 위한 Manager
    manager = multiprocessing.Manager()

    # 명령 Queue
    queueList = manager.list()
    # Error Check용 Dict
    errorDict = manager.dict({'isError': False})

    # Sensor Process
    flask_process = Process(target=run_flask, args=(queueList, errorDict))
    sensor_process = Process(target=run_snesor, args=(queueList, errorDict))

    flask_process.start()
    sensor_process.start()

    flask_process.join()
    sensor_process.join()
