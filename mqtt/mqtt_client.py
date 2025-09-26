import paho.mqtt.client as mqtt


class MQTT_Client():
    
    def __init__(self, host="localhost", port=1883, client_id="test",
                 on_connect=None, on_message=None):
        self.host = host
        self.port = port    
        self.client = mqtt.Client(client_id=client_id) #, callback_api_version=2)
        self.client.connect(host=host, port=port)
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        
    def publih_message(self, topic, message):
        self.client.publish(topic, message)
    
    def disconnect(self):
        self.client.disconnect()