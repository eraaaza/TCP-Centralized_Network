#######################################################################
# File:             client_handler.py
# Author:           Jose Ortiz
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template ClientHandler class. You are free to modify this
#                   file to meet your own needs. Additionally, you are
#                   free to drop this client handler class, and use a version of yours instead.
# Running:          Python 2: python server.py
#                   Python 3: python3 server.py
#                   Note: Must run the server before the client.
########################################################################
import pickle
import threading
from menu import Menu
import datetime

class ClientHandler(object):
    """
    The ClientHandler class provides methods to meet the functionality and services provided
    by a server. Examples of this are sending the menu options to the client when it connects,
    or processing the data sent by a specific client to the server.
    """
    def __init__(self, server_instance, clientsocket, addr):
        """
        Class constructor already implemented for you
        :param server_instance: normally passed as self from server object
        :param clientsocket: the socket representing the client accepted in server side
        :param addr: addr[0] = <server ip address> and addr[1] = <client id>
        """
        self.server_ip = addr[0]
        self.client_id = addr[1]
        self.server = server_instance
        self.clientsocket = clientsocket
        self.server.send_client_id(self.clientsocket, self.client_id)
        self.unreaded_messages = []
        self.print_lock = threading.Lock()  # creates the print lock

    def _sendMenu(self):
        """
        Already implemented for you.
        sends the menu options to the client after the handshake between client and server is done.
        :return: VOID
        """
        menu = Menu()
        data = {'menu': menu}
        self.send(data)

    def process_options(self):
        """
        Process the option selected by the user and the data sent by the client related to that
        option. Note that validation of the option selected must be done in client and server.
        In this method, I already implemented the server validation of the option selected.
        :return:
        """
        #self.print_lock.acquire()
        data = {}
        data = self.receive()
        print(data)
        if 'option_selected' in data.keys() and 1 <= data['option_selected'] <= 6: # validates a valid option selected
            option = data['option_selected']
            if option == 0:
                room_id = data['room_id']
                client_id = data['client_id']
                chat_message = data['message']
                connection_status = data['status']
                self._processes_chat_room_messages(room_id, client_id, chat_message, connection_status)
            elif option == 1:
                self._send_user_list()
            elif option == 2:
                recipient_id = data['recipient_id']
                message = data['message']
                self._save_message(recipient_id, message)
            elif option == 3:
                self._send_messages()
            elif option == 4:
                room_id = data['room_id']
                self._create_chat(room_id)
            elif option == 5:
                room_id = data['room_id']
                self._join_chat(room_id)
            elif option == 6:
                self._disconnect_from_server()
        else:
            print("The option selected is invalid")

        #self.print_lock.release()

    def _send_user_list(self):
        """
        TODO: send the list of users (clients ids) that are connected to this server.
        :return: VOID
        """
        usersOn = self.server.clients
        self.send(usersOn)

    def _save_message(self, recipient_id, message):
        """
        TODO: link and save the message received to the correct recipient. handle the error if recipient was not found
        :param recipient_id:
        :param message:
        :return: VOID
        """
        recipient_id = int(recipient_id)

        if recipient_id in self.server.clients:
            setTime = datetime.datetime.now()
            message = str(setTime) + ": " + message +" (from: " + self.client_id + ")"
            self.server.clients[recipient_id].unread_messages.append(message)
        else:
            message = "Error! Recipient ID was not found."
            self.send(message)

    def _send_messages(self):
        """
        TODO: send all the unreaded messages of this client. if non unread messages found, send an empty list.
        TODO: make sure to delete the messages from list once the client acknowledges that they were read.
        :return: VOID
        """
        message = []
        if len(self.unreaded_messages) == []:
            self.send(message)
        else:
            message = '\n'.join(self.unreaded_messages)
            self.send(message)
            self.delete_client_data()

    def _create_chat(self, room_id):
        """
        TODO: Creates a new chat in this server where two or more users can share messages in real time.
        :param room_id:
        :return: VOID
        """
        chat_room_exist = False

        for obj in self.server.chat_room:
            if obj == room_id:
                chat_room_exist = True
                open_status = False
                self.send(open_status)
                break

        if chat_room_exist == False:
            self.server.chat_owner[room_id] = self.client_id
            self.server.chat_room[room_id] = self.client_id
            open_status = True
            self.send(open_status)

    def _join_chat(self, room_id):
        """
        TODO: join a chat in a existing room
        :param room_id:
        :return: VOID
        """
        chat_room_exist = False

        for obj in self.server.chat_room:
            if obj == room_id:
                chat_room_exist = True
                join_status = True
                self.server.chat_room[room_id] = self.client_id
                self.send(join_status)
                break

        if chat_room_exist == False:
            join_status = False

            self.send(join_status)


    def delete_client_data(self):
        """
        TODO: delete all the data related to this client from the server.
        :return: VOID
        """
        self.unreaded_messages.clear()

    def _disconnect_from_server(self):
        """
        TODO: call delete_client_data() method, and then, disconnect this client from the server.
        :return: VOID
        """
        message = "Bye for now..."
        self.send(message)
        self.clientsocket.close()

    def _processes_chat_room_messages(self, room_id, client_id, chat_messsage, connection_status):
        if connection_status == False and self.server.chat_owner[room_id] != client_id:
            chat_messsage = "DISCONNECT"
            self.send(chat_messsage)
        if connection_status == False and self.server.chat_owner[room_id] == client_id:
            chat_messsage = "DISCONNECT"
            for obj in self.server.chat_room:
                self.server.send(self.server.chat_room[obj], chat_messsage)
        else:
            for obj in self.server.chat_room:
                self.server.send(self.server.chat_room[obj], chat_messsage)

    def send(self, data):
        """
        TODO: Serializes and then sends data to server
        :param data:
        :return:
        """
        data = pickle.dumps(data)  # serialized data
        self.clientsocket.send(data)

    def receive(self, MAX_BUFFER_SIZE=4090):
        """
        TODO: Desearializes the data received by the server
        :param MAX_BUFFER_SIZE: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        raw_data = self.clientsocket.recv(MAX_BUFFER_SIZE)  # deserializes the data from server
        return pickle.loads(raw_data)

    def run(self):
        #self._sendMenu()
        self.process_options()












