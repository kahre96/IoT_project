from bitstring import ConstBitStream, BitArray, ReadError


class parse_message:


    def __init__(self,data):
        self.topic_names = []
        self.m_type = data.read("uint:4")
        self.DUP = data.read("uint:1")
        self.QoS = data.read("uint:2")
        self.Retain = data.read("uint:1")
        self.RL = data.read("uint:8")

        if self.RL != 0:

            if self.m_type == 3:
                topic_len = data.read("uint:16")
                topic_name= ""
                for i in range(topic_len):
                    topic_name += chr(data.read("uint:8"))

                self.topic_names.append(topic_name)
                #readlength= topic_len*8
                #topic_name_hex = data.read(f"hex:{readlength}")
                #self.topic_name = f"string: {bytes.fromhex(topic_name_hex).decode('utf-8')}"
                self.packet_ID = data.read("uint:8")

            # sub or unsub
            if self.m_type == 8 or self.m_type == 10:

                self.pid = data.read("uint:16")
                self.RL -= 2

                stop = 0
                if self.m_type == 8:
                    stop = 1

                while self.RL > stop:


                    topic_len = data.read("uint:16")
                    self.RL -= (2+topic_len)

                    topic_name=""
                    for i in range(topic_len):
                        topic_name += chr(data.read("uint:8"))

                    self.topic_names.append(topic_name)
                    print(topic_name)
