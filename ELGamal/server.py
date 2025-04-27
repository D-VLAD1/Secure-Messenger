"""module for a server"""
import socket
import threading
import random
import math
import re
import hashlib
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
        self.create_keys()


        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")
            self.broadcast(f'new person has joined: {username}')
            self.username_lookup[c] = username
            self.clients.append(c)

            # receive client`s public key
            client_public_key = c.recv(1024).decode()
            self.public_keys[c] = client_public_key

            # send public key to the client
            server_public_key = f"{self.n},{self.e}"
            c.send(server_public_key.encode())

            print(f"{username} has succesfully connected")

            threading.Thread(target=self.handle_client,args=(c,addr,)).start()


    def decode_message(self, c1, c2):
        """Decodes a message using block rsa"""
        s = pow(c1, self.__a, self.p)
        numeric_string = str(pow(c2*pow(s, self.p - 2, self.p), 1, self.p))
        padding_needed = (3 - len(numeric_string) % 3) % 3
        numeric_string = numeric_string.zfill(len(numeric_string)+padding_needed)
        decoded_message = ''.join(chr(int(numeric_string[i:i+3])) for i in range(0, len(numeric_string), 3))
        return decoded_message


    def encode_message(self, message, client_n, client_e):
        """Encodes a message using block rsa"""
        client_block_size = len(str(client_n))-1
        numeric_string = ''.join(f"{ord(c):03d}" for c in message)

        blocks = [numeric_string[i:i+client_block_size] for i in range(0, len(numeric_string), client_block_size)]
        last_block_size = len(blocks[-1])
        encrypted_blocks = [str(pow(int(block), client_e, client_n)).zfill(client_block_size+1) for block in blocks]

        encrypted_message = "".join(encrypted_blocks)
        full_message = f"{encrypted_message}|{last_block_size}"
        return full_message


    def broadcast(self, msg: str):
        """Sends a message to all clients"""
        for client in self.clients:

            # encrypt the message

            pub_key = self.public_keys[client]
            client_n, client_e = map(int, pub_key.split(","))
            encoded_message = self.encode_message(msg, client_n, client_e)

            msg_hash = hashlib.sha256(msg.encode()).hexdigest()
            full_message = f"{msg_hash}|{encoded_message}"
            client.send(full_message.encode())

    def handle_client(self, c: socket, addr):
        """Handles a wanted client"""
        while True:
            sender_name = self.username_lookup[c]
            user_getter = None
            msg = c.recv(1024).decode()

            c1, c2 = msg.split(",")

            decoded_message = self.decode_message(c1, c2)

            # check if hashes are the same
            new_hash = hashlib.sha256(decoded_message.encode()).hexdigest()
            if new_hash != received_hash:
                raise ValueError("Hashes of the same message are not the same!")

            # look to whom is this message for
            match = re.search(r'@\w+:', decoded_message)
            if match:
                user_getter = match.group(0)[:-1]
                message_to_send = decoded_message[match.end():].lstrip()
                message_to_send = f"From @{sender_name}: "+message_to_send
            else:
                raise ValueError("Please, correctly type the name of \
the person you want to send a message to")

            for client in self.clients:
                if self.username_lookup[client] == user_getter[1:]:
                    # get the wanted client`s keys
                    pub_key = self.public_keys[client]
                    client_n, client_e = map(int, pub_key.split(","))
                    encoded_message = self.encode_message(message_to_send, client_n, client_e)

                    msg_hash = hashlib.sha256(message_to_send.encode()).hexdigest()
                    full_message = f"{msg_hash}|{encoded_message}"
                    client.send(full_message.encode())


    @staticmethod
    def is_prime(number) -> bool:
        """Checks if a number is prime"""
        if number <2:
            return False

        for n in range(2, int(math.sqrt(number)+1)):
            if number % n == 0:
                return False
        return True

    @staticmethod
    def generate_prime(min_value, max_value) -> int:
        """Generates a random prime number in given range"""
        prime = random.randint(min_value, max_value)
        while not Server.is_prime(prime):
            prime = random.randint(min_value, max_value)
        return prime

    @staticmethod
    def mod_inverse(e, phi) -> int:
        """Finds an inversed num to e with module phi"""
        for d in range(3, phi):
            if (d*e)%phi == 1:
                return d
        raise ValueError("gcd(e, d) is not 1")

    def create_keys(self):
        """Creates public and private keys for a client"""
        p = self.generate_prime(10**10, 10**14)
        g = self.find_primitive_root(p)
        secret_a = random.randint(2, p-2)
        e = pow(g, secret_a, p)
        self.p, self.g, self.e, self.__a = p, g, e, secret_a

    @staticmethod
    def prime_factors(n):
        """Finds all prime factors of a number n"""
        factors = set()
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.add(d)
                n //= d
            d += 1
        if n > 1:
            factors.add(n)
        return factors

    @staticmethod
    def find_primitive_root(p):
        """Finds a random primitive root of mod p"""
        if p == 2:
            return 1
        factors = Server.prime_factors(p - 1)
        for g in range(2, p):
            flag = True
            for q in factors:
                if pow(g, (p - 1) // q, p) == 1:
                    flag = False
                    break
            if flag:
                return g
        return None

if __name__ == "__main__":
    s = Server(9001)
    s.start()
