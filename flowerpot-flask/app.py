from distutils.util import run_2to3
import multiprocessing
import os
import time
import eventlet
from multiprocessing import Process
from multiprocessing.dummy import Process
from flask import Flask, jsonify
from flask_mqtt import Mqtt
from gpiozero import Motor
from flask_socketio import SocketIO

broker_ip = '127.0.0.1'
mqtt_port = 1883
app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = broker_ip
app.config['MQTT_BROKER_PORT'] = mqtt_port
# app.config['MQTT_USERNAME'] = 'user'
# app.config['MQTT_PASSWORD'] = 'secret'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds

def run_snesor(queue, errorDict):
    motor1 = Motor(forward=17, backward=27)
    motor2 = Motor(forward=22, backward=23)
    motor3 = Motor(forward=5, backward=6)
    motor4 = Motor(forward=13, backward=19)

    # 전진
    @app.route('/forward')
    def move_forward():
        try:
            print('High')
            motor1.forward()
            motor2.forward()
            motor3.forward()
            motor4.forward()
            time.sleep(5)
        except:
            print("Error")
            return jsonify(
                code=500,
                success=False,
                msg='Sensor Connection Error'
            )

        finally:
            motor1.stop()
            motor2.stop()
            motor3.stop()
            motor4.stop()
            return jsonify(
                code=200,
                success=True,
                msg='OK'
            )
            

    # 후진
    @app.route('/back')
    def move_backward():
        try:
            print('Low')
            motor1.backward()
            motor2.backward()
            motor3.backward()
            motor4.backward()
            time.sleep(5)
        except:
            print("Error")
            return jsonify(
                code=500,
                success=False,
                msg='Sensor Connection Error'
            )

        finally:
            motor1.stop()
            motor2.stop()
            motor3.stop()
            motor4.stop()
            return jsonify(
                code=200,
                success=True,
                msg='OK'
            )


def run_flask(queue, errorDict):
    socketio = SocketIO(app)
    mqtt = Mqtt(app)

    topic = ['flowerpot1', 'flowerpot2', 'flowerpot3']
    flowerpot_data = {'flowerpot1': {}, 'flowerpot2': {}, 'flowerpot3': {}}

    @app.route('/')
    def index():
        return jsonify({"index" : 'Hello world!'})

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        if(rc == 0):
            for t in topic :
                mqtt.subscribe(t)
        else:
            print("Bad connection Returned code = ", rc)


    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        list=message.payload.decode().split()
        flowerpot_data
        # Moisture <int> / Light <float>
        # 0         1   2   3       4
        moisture = float(list[1])
        light = float(list[4])
        global_pot_update(message.topic, moisture, light)


    def global_pot_update(inputTopic, moisture, light):
        flowerpot_data
        topic
        print(inputTopic)
        if(inputTopic == topic[0]):
            flowerpot_data[topic[0]]['moisture'] = moisture
            flowerpot_data[topic[0]]['light'] = light
        elif(inputTopic == topic[1]):
            flowerpot_data[topic[1]]['moisture'] = moisture
            flowerpot_data[topic[1]]['light'] = light
        elif(inputTopic == topic[2]):
            flowerpot_data[topic[2]]['moisture'] = moisture
            flowerpot_data[topic[2]]['light'] = light
        else:
            return 0
        print(flowerpot_data)

    @app.route('/flowerpot')
    def get_flowerpot1():
        flowerpot_data
        return jsonify(flowerpot_data)


    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)


if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance
    print("Flower-Pot-Server Runing...\n Pid of main : ", os.getpid())

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