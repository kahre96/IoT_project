

class mqtt_message:

    def __init__(self,type, pid=None):
        if pid is not None:
            self.Pid = format(pid, '04x')
        RL = self.calc_remaining_length(type)
        self.hex_mes = f"{hex(type)}0 {RL}"
        self.byte_mes = bytes.fromhex(self.hex_mes[2:])


    def calc_remaining_length(self,typecode):
        if typecode == 2:
            RL = "02 00 00"
        elif typecode == 9:
            RL = f"03{self.Pid} 00"
        elif typecode == 11:
            RL = f"02 {self.Pid}"
        else:
            RL = "00"

        return RL
