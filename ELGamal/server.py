"""module for a server"""
import socket
import threading
import random
import math
import re
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
        self.create_keys()
        print("Keys generated")
        print(f"My P: {self.p}")
        print(f"My G: {self.g}")
        print(f"My E: {self.e}")
        print(f"My secret A: {self.__a}")


        while True:
            c, addr = self.s.accept()
            username = c.recv(1024).decode()
            print(f"{username} tries to connect")
            self.broadcast(f'n :{username}')
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


    def decode_message(self, c1, c2):
        """Decodes a message using ELGamal algorithm"""
        print(f"c1: {c1}")
        print(f"c2: {c2}")
        s = pow(c1, self.__a, self.p)
        print(f"s: {s}")
        numeric_string = str(pow(c2*pow(s, self.p - 2, self.p), 1, self.p))
        padding_needed = (3 - len(numeric_string) % 3) % 3
        numeric_string = numeric_string.zfill(len(numeric_string)+padding_needed)
        print(f"Numeric string: {numeric_string}")
        decoded_message = ''.join(chr(int(numeric_string[i:i+3])) for i in range(0, len(numeric_string), 3))
        print(f"Decoded: {decoded_message}")
        return decoded_message


    def encode_message(self, message, client_p, client_g, client_e):
        """Encodes a message for a specific client using ELGamal algo"""
        numeric_string = ''.join(f"{ord(c):03d}" for c in message)
        print(f"Numeric string: {numeric_string}")
        k = random.randint(2, client_p-2)
        print(f"Random k: {k}")
        c1 = pow(client_g, k, client_p)
        print(f"c1: {c1}")
        c2 = pow(int(numeric_string)*pow(client_e, k, client_p), 1, client_p)
        print(f"c2: {c2}")
        message_to_send = f"{c1},{c2}"
        return message_to_send


    def broadcast(self, msg: str):
        """Sends a message to all clients"""
        for client in self.clients:

            # encrypt the message
            print(f"Encrypting: {msg}")
            pub_key = self.public_keys[client]
            client_p, client_g, client_e = map(int, pub_key.split(","))
            encoded_message = self.encode_message(msg, client_p, client_g, client_e)
            print(f"Ecrypted msg: {encoded_message}")
            client.send(encoded_message.encode())

    def handle_client(self, c: socket, addr):
        """Handles a wanted client"""
        while True:
            sender_name = self.username_lookup[c]
            user_getter = None
            msg = c.recv(1024).decode()

            print(f"Message to decode: {msg}")
            c1, c2 = map(int, msg.split(","))

            decoded_message = self.decode_message(c1, c2)
            print(f"Decoded msg: {decoded_message}")
            # look to whom is this message for
            match = re.search(r'@\w+:', decoded_message)
            if match:
                user_getter = match.group(0)[:-1]
                message_to_send = decoded_message[match.end():].lstrip()
                message_to_send = f"F@{sender_name}:"+message_to_send
            else:
                raise ValueError("Please, correctly type the name of \
the person you want to send a message to")

            for client in self.clients:
                if self.username_lookup[client] == user_getter[1:]:
                    # get the wanted client`s keys
                    pub_key = self.public_keys[client]
                    client_p, client_g, client_e = map(int, pub_key.split(","))
                    print(f"Encoding for {client}: {message_to_send}")
                    encoded_message = self.encode_message(message_to_send, client_p, client_g, client_e)
                    print(f"Encoded message for {client}: {encoded_message}")
                    client.send(encoded_message.encode())


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
        while not Server.miller_rabin(prime):
            prime += 1
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
        print("Generating p...")
        p = self.generate_prime(10**20, 10**21)
        print("Generated")
        print("Generating g...")
        g = self.find_primitive_root(p)
        print("Generated")
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
        factors = Server.prime_factors(p - 1)
        while True:
            g = random.randint(2, p-2)
            if all(pow(g, (p-1)//q, p) != 1 for q in factors):
                return g
        # for g in range(2, p):
        #     flag = True
        #     for q in factors:
        #         if pow(g, (p - 1) // q, p) == 1:
        #             flag = False
        #             break
        #     if flag:
        #         return g
        return None


    @staticmethod
    def miller_rabin(n, k=100):
        """
        Function to check if a number is prime using Miller-Rabin primality test.

        n: int - The number to check for primality.
        k: int - The number of iterations for accuracy.
        Returns True if n is probably prime, False if n is composite.
        """
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False

        r, d = 0, n - 1
        while d % 2 == 0:
            d //= 2
            r += 1

        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)

            if x == 1 or x == n - 1:
                continue

            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False

        return True


if __name__ == "__main__":
    s = Server(9001)
    s.start()
