import tkinter as tk
from tkinter import ttk
import threading
from collections import defaultdict
from paho.mqtt import client as mqtt_client
import time

subscribed_channels = []
channel_content = defaultdict(list)
channel_average = defaultdict(lambda: [0.0, 0, 0, 0, 0.0])

def subscribe(client: mqtt_client, topic, obj):
    def on_message(client, userdata, msg):

        text = msg.payload.decode()
        text = text.split('#')
        delay= time.time() - float(text[0])
        values = float(text[0]),delay, int(text[1]), int(text[2]), int(text[3]), int(text[4])
        channel_content[msg.topic].append(values)
        threading.Thread(update_averages(topic))
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if obj.current_channel== msg.topic:
            obj.show_content(channel=msg.topic)

    client.subscribe(topic)
    client.on_message = on_message


def update_averages(topic):

    if len(channel_content[topic]) == 0:
        return
    sum_delay = 0.0
    sum_temp = 0
    sum_hum = 0
    sum_pow = 0
    sum_on_off = 0.0
    for i in channel_content[topic]:
        sum_delay += i[1]
        sum_temp += i[2]
        sum_hum += i[3]
        sum_pow += i[4]
        sum_on_off += i[5]

    channel_average[topic][0] = sum_delay / len(channel_content[topic])
    channel_average[topic][1] = sum_temp / len(channel_content[topic])
    channel_average[topic][2] = sum_hum / len(channel_content[topic])
    channel_average[topic][3] = sum_pow / len(channel_content[topic])
    channel_average[topic][4] = sum_on_off / len(channel_content[topic])




class myGUI:
    def __init__(self, window, client):

        self.window = window
        self.subscribed_channels = []
        self.client= client
        self.current_channel=None


        # Create a frame to hold the subscribe button and entry field
        subscribe_frame = tk.Frame(self.window)

        # Create a button to subscribe to a new channel
        subscribe_button = ttk.Button(subscribe_frame, text="Subscribe", command=self.handle_subscribe)
        subscribe_button.pack(side=tk.LEFT)

        # Create an entry field to enter the channel to subscribe to
        self.entry_field = ttk.Entry(subscribe_frame)
        self.entry_field.pack(side=tk.LEFT)

        # Pack the subscribe frame to show the button and entry field
        subscribe_frame.pack()



        # Create a frame to hold the channel buttons
        self.button_frame = ttk.Frame(self.window)

        # Add the channel buttons to the frame
        self.update_buttons()

        # Pack the frame to show the buttons
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create a text field to display the content of the selected subscription topic
        self.text_field = tk.Text(self.window)
        self.text_field.pack(side=tk.TOP)

        self.text_field2 = tk.Text(self.window, height=5)
        self.text_field2.pack(side=tk.BOTTOM)

    def handle_subscribe(self):
        # Get the channel to subscribe to from the entry field
        channel = self.entry_field.get()
        # Add the channel to the list of subscribed channels
        self.subscribed_channels.append(channel)
        subscribe(client=self.client, topic=channel, obj=self)
        # Clear the entry field
        self.entry_field.delete(0, tk.END)
        # Update the list of buttons to show the new subscribed channel
        self.update_buttons()

    def update_buttons(self):
        # Clear the frame that holds the channel buttons
        for widget in self.button_frame.winfo_children():
          widget.destroy()
        # Add the channel buttons to the frame
        for channel in self.subscribed_channels:
          button = ttk.Button(self.button_frame, text=channel, command=lambda c=channel: [self.show_content(c),self.update_current(c)])
          button.pack()
        # Pack the frame to show the buttons
        self.button_frame.pack()

    def update_current(self, current):
        self.current_channel = current

    def show_content(self, channel):
        # Clear the text field
        self.text_field.delete(1.0, tk.END)
        self.text_field2.delete(1.0, tk.END)
        # Get the content for the selected channel
        content = self.get_content(channel)
        averages = self.get_averages(channel)
        # Insert the content into the text field
        for i in content:
            self.text_field.insert(tk.END, f'{i}\n')

        self.text_field2.insert(tk.END, averages)

    def get_content(self, channel):
        return channel_content[channel]

    def get_averages(self, channel):

        f1 = f'avg delay:{channel_average[channel][0]}\n'
        f2 = f'avg temp:{channel_average[channel][1]}\n'
        f3 = f'avg humidity:{channel_average[channel][2]}\n'
        f4 = f'avg pressure:{channel_average[channel][3]}\n'
        f5 = f'avg on time:{channel_average[channel][4]}\n'

        return f1+f2+f3+f4+f5
