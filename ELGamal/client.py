"""module for clients"""
import socket
import threading
import random
import math

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
        self.create_keys()
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
            c1, c2 = map(int, message.split(","))
            s = pow(c1, self.__a, self.p)
            numeric_string = str(pow(c2*pow(s, self.p - 2, self.p), 1, self.p))
            print(f"Numeric string: {numeric_string}")
            padding_needed = (3 - len(numeric_string) % 3) % 3
            numeric_string = numeric_string.zfill(len(numeric_string)+padding_needed)
            decoded_message = ''.join(chr(int(numeric_string[i:i+3])) for i in range(0, len(numeric_string), 3))
            print(decoded_message)

    def write_handler(self):
        """Writes a message and encrypts it using ELGamal encoding"""
        while True:
            message = input()
            print(f"Encoding: {message}")
            numeric_string = ''.join(f"{ord(c):03d}" for c in message)
            print(f"Numeric string: {numeric_string}")
            k = random.randint(2, self.server_p-2)
            c1 = pow(self.server_g, k, self.server_p)
            c2 = pow(int(numeric_string)*pow(self.server_e, k, self.server_p), 1, self.server_p)

            message_to_send = f"{c1},{c2}"
            print(f"Sending: {message_to_send}")
            self.s.send(message_to_send.encode())

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
        while not Client.miller_rabin(prime):
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
        p = self.generate_prime(10**20, 10**21)
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
        factors = Client.prime_factors(p - 1)
        for g in range(2, p):
            flag = True
            for q in factors:
                if pow(g, (p - 1) // q, p) == 1:
                    flag = False
                    break
            if flag:
                return g
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
    cl = Client("127.0.0.1", 9001, "ng")
    cl.init_connection()
