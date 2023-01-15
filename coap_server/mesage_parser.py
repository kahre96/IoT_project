import bitstring
from bitstring import ConstBitStream, BitArray, ReadError


class Message:

    def __init__(self):
        self.version = None
        self.T = None
        self.tkl = None
        self.code = None
        self.m_id = None
        self.payload = ""
        self.opt = []


    def add_opt(self,option):
        self.opt.append(option)



def message_parser(data):
    MC = Message()

    bits = BitArray(data)
    s = ConstBitStream(bits)

    MC.version = s.read('int:2')
    MC.T = s.read('int:2')
    MC.tkl = s.read('bin:4')
    MC.code = s.read('int:8')
    MC.m_id = s.read('uint:16')

    # parse options
    # looks for ff after each option to end options
    optionnr = 1
    optioncounter = 0
    try:
        s.peek('hex:8')
    except bitstring.ReadError:
        return MC

    while True:

        try:
            if s.peek('hex:8') == 'ff':
                # step past delimitor/end of options and go out of options
                delim = s.read('hex:8')
                break

            optiondelta = s.read('uint:4')
            optionlength = s.read('uint:4')

            # read extended optiondelta
            if optiondelta == 14:
                optiondelta = s.read('uint:16') + 269

            if optiondelta == 13:
                optiondelta = s.read('uint:8') + 13
            optioncounter += optiondelta

            # read extended optionlength
            if optionlength == 14:
                optionlength = s.read('uint:16') + 269
            if optionlength == 13:
                optionlength = s.read('uint:8') + 13

            readlength = optionlength * 8
            optvalue = s.read(f'hex:{readlength}')

            opaqueopt = (1, 4)
            stringopts = (3, 8, 11, 15, 20, 35, 39)
            uintopts = (7, 12, 14, 17, 28, 60)
            blockopts = (23, 27)
            if optvalue == '':
                valuestring = ""
            elif optioncounter in opaqueopt:
                valuestring = f"{optvalue}"
            elif optioncounter in stringopts:
                valuestring = f"{bytes.fromhex(optvalue).decode('utf-8')}"
            elif optioncounter in uintopts:
                valuestring = f"{int(optvalue, 16)}"
            elif optioncounter in blockopts:
                valuestring = "its a block"
            else:
                valuestring = "could not read value"
            # valuestring = codecs.decode(optvalue, "hex").decode('utf-8')
            # valuestring = optvalue.decode("utf-8")
            optdict={
                'option': optioncounter,
                'optionLength': optionlength,
                'optionvalue': valuestring
            }
            MC.add_opt(optdict)
            print("optionnr: ", optionnr)
            print("optioncode: ", optioncounter)
            print("optionlength: ", optionlength)
            print("optionvalue: ", valuestring)

            optionnr += 1

        except ReadError:
            # print(ReadError)
            # print("cant read optionvalue, ignore if option was empty")
            break


    # insert the rest into the payload

    # tries to read remain bits over and over until theres no more then break and move on
    while True:
        try:
            temp = s.read('hex:8')

            MC.payload += bytes.fromhex(temp).decode('utf-8')
        except ReadError:
            break
        except TypeError:
            break

    print("Payload:", MC.payload)
    return MC
