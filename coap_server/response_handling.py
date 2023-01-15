import random
import time
from bitstring import ConstBitStream, BitArray, ReadError
from mesage_parser import message_parser, Message
import socket


Resource = {
    "temp": "25",
    "Humidity": "26",
    "pow": "1200",
    "onoff": "1",

    "all": ""


}


# changes the values once every 5 seconds
def update_values():
    while True:
        t =random.randint(0, 500)
        # print(t)
        Resource['temp'] = f'{t}'

        hum = random.randint(0,100)
        Resource['hum'] = f'{hum}'

        pow = random.randint(0, 3000)
        Resource['pow'] = f'{pow}'

        onoff = random.uniform(0,1)
        if onoff < 0.1:
            if Resource['onoff'] == "1":
                Resource['onoff'] = "0"
            else:
                Resource['onoff'] = "1"

        Resource['all'] = f"#{t}#{hum}#{pow}#{Resource['onoff']}"
        time.sleep(5)




def sendMessage(type, payload, address, mid, socket):

    MesID = hex(mid)
    PL = payload.encode('utf-8').hex()
    Message = f"50 {type} {MesID[2:]} c0 ff {PL}"

    bytesToSend = bytes.fromhex(Message)

    socket.sendto(bytesToSend, address)

def get_handler(message, address, socket):

    URI = message.opt[0]['optionvalue']
    if URI == "time":
        PL = time.time()
    elif URI == "all":
       PL= f"{time.time()} {Resource[URI]}"
    else:
        try:
            PL = Resource[URI]
        except KeyError:
            PL="Could not find resource"

    sendMessage(type="45", payload=PL, address=address, mid=message.m_id, socket=socket)


# handels both put and post now
def post_handler(message,address, socket):

    URI = message.opt[0]['optionvalue']

    # the post should ofcourse append values rather than replace
    # but makes no sense to have multiple values on nay of these resources
    # so put and post will just do the same here
    try:
        Resource[URI] = message.payload
        PL = f"{URI} was changed to {message.payload}"

    except KeyError:
        PL= f"could not find resource"

    sendMessage(type="44", payload=PL, address=address, mid=message.m_id, socket=socket)


def delete_handler(message,address, socket):
    URI = message.opt[0]['optionvalue']

    try:
        Resource[URI] = ""
        PL=f"{URI} was deleted"
    except KeyError:
        PL= "could not find resource"

    sendMessage(type="42", payload=PL, address=address, mid=message.m_id, socket=socket)

def threaded_response_handling(data, address,socket):


    message = message_parser(data)

    if message.code == 1:
        get_handler(message, address, socket)

    if message.code == 2 or message.code == 3:
        post_handler(message,address, socket)

    if message.code == 4:
        delete_handler(message,address, socket)


