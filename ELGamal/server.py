"""module for a server"""
import socket
import threading
import re
from utils import *
import ast
class Server:
    """Server"""

    def __init__(self, port: int) -> None:
        self.host = '127.0.0.1'
        self.port = port
        self.clients = []
        self.username_lookup = {}
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.public_keys = {}

    def start(self):
        self.s.bind((self.host, self.port))
        self.s.listen(100)

        # generate keys ...
        print("Generating keys...")
        self.p, self.g, self.e, self.__a = create_keys()
        print("Keys generated")
        print(f"My P: {self.p}")
        print(f"My G: {self.g}")
        print(f"My E: {self.e}")
        print(f"My secret A: {self.__a}")


        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")
            self.broadcast(f'New person :{username}')
            self.username_lookup[c] = username
            self.clients.append(c)

            # receive client`s public key
            print(f"Receiving {self.username_lookup[c]} keys...")
            client_public_key = c.recv(1024).decode()
            self.public_keys[c] = client_public_key
            print("Received")

            # send public key to the client
            server_public_key = f"{self.p},{self.g},{self.e}"
            c.send(server_public_key.encode())

            print(f"{username} has succesfully connected")

            threading.Thread(target=self.handle_client,args=(c,addr,)).start()

    def broadcast(self, msg: str):
        """Sends a message to all clients"""
        for client in self.clients:

            # encrypt the message
            print(f"Encrypting: {msg}")
            pub_key = self.public_keys[client]
            client_p, client_g, client_e = map(int, pub_key.split(","))
            encrypted_blocks, last_block_len = encode_message(msg, client_p, client_g, client_e)
            message_to_send = f"{encrypted_blocks}|{last_block_len}"
            print(f"Ecrypted msg: {message_to_send}")
            client.send(message_to_send.encode())

    def handle_client(self, c: socket, addr):
        """Handles a wanted client"""
        while True:
            sender_name = self.username_lookup[c]
            user_getter = None
            msg = c.recv(1024).decode()

            print(f"Message to decode: {msg}")
            encypted_msg, last_block_len = msg.split("|")
            decoded_message = decode_message(ast.literal_eval(encypted_msg), ast.literal_eval(last_block_len),
                                              self.p, self.__a)
            print(f"Decoded msg: {decoded_message}")
            # look to whom is this message for
            match = re.search(r'@\w+:', decoded_message)
            if match:
                user_getter = match.group(0)[:-1]
                message_to_send = decoded_message[match.end():].lstrip()
                message_to_send = f"From @{sender_name}:"+message_to_send
            else:
                raise ValueError("Please, correctly type the name of \
the person you want to send a message to")

            for client in self.clients:
                if self.username_lookup[client] == user_getter[1:]:
                    # get the wanted client`s keys
                    pub_key = self.public_keys[client]
                    client_p, client_g, client_e = map(int, pub_key.split(","))
                    print(f"Encoding for {client}: {message_to_send}")
                    encrypted_blocks, last_block_len = encode_message(message_to_send, client_p,
                                                                    client_g, client_e)
                    message_to_send = f"{encrypted_blocks}|{last_block_len}"
                    print(f"Encoded message for {client}: {message_to_send}")
                    client.send(message_to_send.encode())


if __name__ == "__main__":
    s = Server(9001)
    s.start()
