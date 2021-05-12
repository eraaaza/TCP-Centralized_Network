#######################################################################
# File:             client.py
# Author:           Jose Ortiz
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template client class. You are free to modify this
#                   file to meet your own needs. Additionally, you are 
#                   free to drop this client class, and add yours instead. 
# Running:          Python 2: python client.py 
#                   Python 3: python3 client.py
#
########################################################################
import socket
import pickle
from menu import Menu

class Client(object):
    """
    The client class provides the following functionality:
    1. Connects to a TCP server 
    2. Send serialized data to the server by requests
    3. Retrieves and deserialize data from a TCP server
    """

    def __init__(self):
        """
        Class constractpr
        """
        # Creates the client socket
        # AF_INET refers to the address family ipv4.
        # The SOCK_STREAM means connection oriented TCP protocol.
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientid = 0
        self.connection = True

    def get_client_id(self):
        data = self.receive()  # deserialized data
        client_id = data['clientid']  # extracts client id from data
        self.clientid = client_id  # sets the client id to this client
        return self.clientid

    #def get_menu(self):
        #data = self.receive()
        #menu = data['menu']
        #self.menu = menu
        #self.menu.set_client(self)
        #return self.menu

    def connect(self, host="127.0.0.1", port=12000):
        """
        TODO: Connects to a server. Implements exception handler if connection is resetted. 
	    Then retrieves the cliend id assigned from server, and sets
        :param host: 
        :param port: 
        :return: VOID
        """
        host = input("Enter the server IP Address:")
        port = int(input("Enter the server port:"))
        user = input("Your id key (i.e. your name):")
        self.clientSocket.connect((host, port))
        print("Successfully connected to server: " + host + '/' + str(port))
        print("Your client info is:")
        print("Client Name: " + user)
        print("Client ID: " + str(self.get_client_id()))

        menu = Menu()
        menu.set_client(self)

        while self.connection == True:
            menu.show_menu()
            menu.process_user_data()

        self.close()

    def send(self, data):
        """
        TODO: Serializes and then sends data to server
        :param data:
        :return:
        """
        data = pickle.dumps(data)  # serialized data
        self.clientSocket.send(data)

    def receive(self, MAX_BUFFER_SIZE=4090):
        """
        TODO: Desearializes the data received by the server
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        raw_data = self.clientSocket.recv(MAX_BUFFER_SIZE)  # deserializes the data from server
        return pickle.loads(raw_data)

    def close(self):
        """
        TODO: close the client socket
        :return: VOID
        """
        self.clientSocket.close()

if __name__ == '__main__':
    client = Client()
    client.connect()
