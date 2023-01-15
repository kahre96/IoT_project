import socket
from bitstring import ConstBitStream, BitArray, ReadError


#sends and recives coap messages
def coap_client(methodcode, uri, messageID, payload="", contenttype="", serverAddressPort=("localhost", 5683)):

    uri_path = ""
    body = ""
    contentopt= ""

    # adds uri path to options if there is one
    if uri != "":
        urilen = len(uri)
        optionhex = uri.encode('utf-8').hex()
        uri_path = f"b{urilen} {optionhex}"

    # add the contenttype
    if contenttype != "":
        content = ""
        if contenttype == 0:
            contentlength = 0
        else:
            contentlength = 1
            content = hex(contenttype)

        contentopt= f"1{contentlength}{content[2:]}"

    MesID= hex(messageID)

    # check if chosen method is post/put and if os adds the payload
    if methodcode == '2' or methodcode == '3':
        pay_load = payload.encode('utf-8').hex()
        body = f"ff {pay_load}"

    # the request message is in the form of a hexstring
    msgFromClient = f"50 0{methodcode} {MesID[2:]} {uri_path} {contentopt}{body}"

    #covert the hexvalues to bytes cause the sendto function needs the data in byte format
    bytesToSend = bytes.fromhex(msgFromClient)



    #buffer
    packet = bytearray(4096)

    #socket
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom_into(packet)

    # remove empty part of buffer
    byte2 = bytes(3)
    header, body = packet.split(byte2, 1)


    # covert recived content into a bitstream and grabs the bits for different part of the coap message
    bits = BitArray(header)

    s = ConstBitStream(bits)

    print("version: ", s.read('int:2'))
    print("T: ", s.read('int:2'))
    print("TKL: ", s.read('bin:4'))
    print("Response Code: ", s.read('int:3'), ".", s.read('int:5'))
    print("Message ID: ", s.read('uint:16'))


    # parse options
    #looks for ff after each option to end options
    optionnr = 1
    optioncounter = 0
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
                optiondelta = s.read('uint:16') +269

            if optiondelta == 13:
                optiondelta = s.read('uint:8') +13
            optioncounter += optiondelta

            # read extended optionlength
            if optionlength == 14:
                optionlength = s.read('uint:16') + 269
            if optionlength == 13:
                optionlength = s.read('uint:8') + 13
            
            readlength = optionlength*8
            optvalue = s.read(f'hex:{readlength}')

            opaqueopt = (1, 4)
            stringopts = (3, 8, 11, 15, 20, 35, 39)
            uintopts = (7, 12, 14, 17, 28, 60)
            blockopts = (23, 27)
            if optvalue == '':
                valuestring = ""
            elif optioncounter in opaqueopt:
                valuestring = f"opaque: {optvalue}"
            elif optioncounter in stringopts:
                valuestring = f"string: {bytes.fromhex(optvalue).decode('utf-8')}"
            elif optioncounter in uintopts:
                valuestring = f"uint: {int(optvalue, 16)}"
            elif optioncounter in blockopts:
                valuestring = "its a block"
            else:
                valuestring = "could not read value"
            #valuestring = codecs.decode(optvalue, "hex").decode('utf-8')
            #valuestring = optvalue.decode("utf-8")
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
    message_content = ""
    while True:
        try:
            temp = s.read('hex:8')
            message_content += bytes.fromhex(temp).decode('utf-8')
        except ReadError:
            break

    print("Payload:", message_content)
    return message_content

