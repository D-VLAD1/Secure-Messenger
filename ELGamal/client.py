"""module for clients"""
import socket
import threading
import random
from utils import *
import ast
class Client:
    """Clients info"""
    def __init__(self, server_ip: str, port: int, username: str) -> None:
        self.server_ip = server_ip
        self.port = port
        self.username = username

    def init_connection(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.connect((self.server_ip, self.port))
        except Exception as e:
            print("[client]: could not connect to server: ", e)
            return

        self.s.send(self.username.encode())

        # create key pairs
        print("Generating keys...")
        self.p, self.g, self.e, self.__a = create_keys()
        print("Keys generated")
        print(f"My P: {self.p}")
        print(f"My G: {self.g}")
        print(f"My E: {self.e}")
        print(f"My secret A: {self.__a}")

        # exchange public keys
        public_key = f"{self.p},{self.g},{self.e}"
        self.s.send(public_key.encode())
        print("Sent my keys to the server")

        # receive the encrypted secret key
        print(f"Receiving server keys...")
        server_public_key = self.s.recv(1024).decode()
        self.server_p, self.server_g, self.server_e = map(int, server_public_key.split(","))
        print("Received")

        message_handler = threading.Thread(target=self.read_handler,args=())
        message_handler.start()
        input_handler = threading.Thread(target=self.write_handler,args=())
        input_handler.start()

    def read_handler(self):
        """Reads an encrypted message"""
        while True:

            message = self.s.recv(1024).decode()
            print(f"Received message:{message}")
            encypted_msg, last_block_len = message.split("|")
            decoded_message = decode_message(ast.literal_eval(encypted_msg), ast.literal_eval(last_block_len),
                                              self.p, self.__a)
            print(decoded_message)

    def write_handler(self):
        """Writes a message and encrypts it using ELGamal encoding"""
        while True:
            message = input()
            encrypted_blocks, last_block_len = encode_message(message, self.server_p,
                                                              self.server_g, self.server_e)
            message_to_send = f"{encrypted_blocks}|{last_block_len}"
            print(f"Sending: {message_to_send}")
            self.s.send(message_to_send.encode())

if __name__ == "__main__":
    cl = Client("127.0.0.1", 9001, "police")
    cl.init_connection()
