import socket
import threading as t
from response_handling import threaded_response_handling,update_values


def main():

    t.Thread(target=update_values).start()
    # Create the socket
    UDPsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to a local address and port
    server_address = ('localhost', 5683)
    UDPsocket.bind(server_address)

    print("server is up and running")
    # Enter the main loop
    while True:
        # Wait for a client to send data
        data, address = UDPsocket.recvfrom(4096)

        #threaded_response_handling(data,address,UDPsocket)
        newclient = t.Thread(target=threaded_response_handling, args=(data,address,UDPsocket))
        newclient.start()

        print(data)
        print(address)

        # Process the data here
        # ...

        # Send a response back to the client
        #sock.sendto(response, address)

if __name__ == "__main__":
    main()
