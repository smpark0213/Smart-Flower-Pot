import json
import eventlet
from flask import Flask, render_template, jsonify
from flask_mqtt import Mqtt
from flask_bootstrap import Bootstrap
# from flask_socketio import SocketIO

broker_ip = '127.0.0.1'
mqtt_port = 1883
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = broker_ip
app.config['MQTT_BROKER_PORT'] = mqtt_port
# app.config['MQTT_USERNAME'] = 'user'
# app.config['MQTT_PASSWORD'] = 'secret'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds

mqtt = Mqtt(app)
# socketio = SocketIO(app)

class Pot:
    def __init__(self, topic, moisture, light):
        self.topic = topic
        self.moisture = moisture
        self.light = light


topic = ['flowerpot1', 'flowerpot2', 'flowerpot3']
global_data = {'flowerpot1': {}, 'flowerpot2': {}, 'flowerpot3': {}}


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
    global global_data
    # Moisture <int> / Light <float>
    # 0         1   2   3       4
    moisture = float(list[1])
    light = float(list[4])
    global_pot_update(message.topic, moisture, light)
    # data = dict(
    #     topic=message.topic,
    #     moisture= moisture,
    #     light= light
    # )
    # socketio.emit('mqtt_message', data=data)


def global_pot_update(inputTopic, moisture, light):
    global global_data
    global topic
    print(inputTopic)
    if(inputTopic == topic[0]):
        global_data[topic[0]]['moisture'] = moisture
        global_data[topic[0]]['light'] = light
    elif(inputTopic == topic[1]):
        global_data[topic[1]]['moisture'] = moisture
        global_data[topic[1]]['light'] = light
    elif(inputTopic == topic[2]):
        global_data[topic[2]]['moisture'] = moisture
        global_data[topic[2]]['light'] = light
    else:
        return 0
    print(global_data)
    return 1


@app.route('/flowerpot')
def get_flowerpot1():
    global global_data
    return jsonify(global_data)

if __name__ == '__main__':
    # important: Do not use reloader because this will create two Flask instances.
    # Flask-MQTT only supports running with one instance
    # socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=False)
    app.run(host='0.0.0.0', debug=True)