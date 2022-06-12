const mqtt = require('mqtt');

const mqtt_options = {
    host: 'localhost',
    port: 1883
};

function connectMqtt() {
    return mqtt.connect(mqtt_options)
}

module.exports = {
    connectMqtt
}