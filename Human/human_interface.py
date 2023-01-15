import random
from paho.mqtt import client as mqtt_client
import tkinter as tk
from gui import myGUI
import sv_ttk




def con_mqtt_client():
    broker="localhost"
    port = 1883
    client_id = f'python-mqtt-{random.randint(0, 1000)}'

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def main():
    client = con_mqtt_client()

    client.loop_start()

    window = tk.Tk()
    window.title("Human interface")

    sv_ttk.set_theme("dark")
    gui = myGUI(window,client)
    window.mainloop()




if __name__ == "__main__":
    main()