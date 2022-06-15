const mqtt = require('mqtt');

const mqtt_options = {
    host: 'arkpi.local',
    port: 1883,
    clientId: `mqtt_${Math.random().toString(16).slice(3)}`,
    keepalive: 1000
};

function connectMqtt() {
    return mqtt.connect(mqtt_options)
}

module.exports = {
    connectMqtt
}