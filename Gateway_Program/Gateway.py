from coap import coap_client
import random
import threading
import time
from paho.mqtt import client as mqtt_client

broker = "localhost"
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'


class values:
    temp = 0
    topic = f"sensor_{client_id}"

#async update of coap
def update_coap(SAP=("localhost",5683)):
    while True:
        MesID = random.randint(4096, 65535)
        temp = coap_client(1, "all", MesID, serverAddressPort=SAP)
        values.temp = temp
        time.sleep(10)


def con_mqtt_client():


    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker! as {client_id}")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 0
    while True:
        time.sleep(5)
        MesID = random.randint(4096, 65535)
        values.temp = coap_client(1, "all", MesID, serverAddressPort=("localhost", 5683))
        msg = f"messages: {msg_count}"
        result = client.publish(values.topic, values.temp)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{values.topic}` containing {values.temp}")
        else:
            print(f"Failed to send message to topic {values.topic}")
        msg_count += 1


def main():
    client = con_mqtt_client()

    sensor1=("localhost", 5683)

    client.loop_start()
    threading.Thread(target=publish, args=(client,)).start()
    threading.Thread(target=update_coap(sensor1)).start()



if __name__ == "__main__":
    main()