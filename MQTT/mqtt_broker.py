import socket
from mqtt_message import mqtt_message
import threading as t
from bitstring import ConstBitStream
from mqtt_parsers import parse_message
from collections import defaultdict


class Mqtt:

    def __init__(self):
        print("creating mqtt class")
        self.topics = defaultdict(list) # tuple topicid,subbed sockets list
        self.retain = {}

    def run(self):
        TCPSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        TCPSocket.bind(('localhost', 1883))
        TCPSocket.listen()
        print("server is up")
        while True:

            client, address = TCPSocket.accept()

            newclient = t.Thread(target=self.threaded_client, args=(client,))
            newclient.start()

    def threaded_client(self, connection):

        while True:
            try:
                data = connection.recv(1024)
            except ConnectionResetError:
                break

            if not data:
                break
            if data:
                bstream = ConstBitStream(data)

                message = parse_message(bstream)
                print(message.m_type)

                if message.m_type == 14:
                    for con in self.topics.values():
                        try:
                            con.remove(connection)
                        except ValueError:
                            pass
                    break
                elif message.m_type == 1:
                    ack_mes = mqtt_message(2)
                    connection.send(ack_mes.byte_mes)
                elif message.m_type == 12:
                    ping_resp = mqtt_message(13)
                    connection.send(ping_resp.byte_mes)
                elif message.m_type == 8:
                    print("subbing")
                    for i in message.topic_names:
                        try:
                            connection.send(self.retain[i])
                        except:
                            print("could not send retain")
                        if i in self.topics:
                            self.topics[i].append(connection)
                        else:
                            self.topics[i] = [connection]
                    suback_mes = mqtt_message(9, message.pid)
                    connection.send(suback_mes.byte_mes)
                elif message.m_type == 10:
                    print("unsubbing")
                    for i in message.topic_names:
                        self.topics[i].remove(connection)
                    unsuback_mes = mqtt_message(11, message.pid)
                    connection.send(unsuback_mes.byte_mes)
                elif message.m_type == 3:
                    print(f"publihing to {message.topic_names[0]}")
                    if message.Retain == 1:
                        self.retain[message.topic_names[0]] = data
                    for connections in self.topics[message.topic_names[0]]:

                        try:
                            connections.send(data)
                        except:
                            for con in self.topics.values():
                                try:
                                    con.remove(connections)
                                except ValueError:
                                    pass

        connection.close()
