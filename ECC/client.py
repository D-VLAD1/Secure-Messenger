import random
import utils
from sympy.ntheory import sqrt_mod
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class Curve:
    """
    The curve class
    """
    def __init__(self, a, b, mod):
        self.a = a
        self.b = b
        self.mod = mod


class Point:
    """
    The Point class
    """
    def __init__(self, x, y, curve):
        self.x = x
        self.y = y
        self.curve = curve

    def __add__(self, other):
        """
        Implements points' addition

        :param other: Point
        :return: Point
        """
        if not isinstance(other, Point):
            raise ValueError('Not a Point')

        mod = self.curve.mod

        if self.x == other.x:
            if self.y == 0:
                return None
            k = ((3 * pow(self.x, 2) + self.curve.a) * pow(2 * self.y, -1, mod)) % mod

        else:
            k = ((other.y - self.y) * pow(other.x - self.x, -1, mod)) % mod

        x3 = (k ** 2 - self.x - other.x) % mod
        y3 = (k * (self.x - x3) - self.y) % mod

        return Point(x3, y3, self.curve)

    def __mul__(self, k):
        """
        Implements point multiple addition

        :param k: int, how many times to add
        :return: Point
        """
        if not isinstance(k, int):
            raise ValueError('Not am integer')

        result, temp = None, self

        for bit in map(int, bin(k)[:1:-1]):
            if bit == 1:
                if result is None:
                    result = temp
                else:
                    result = result + temp
            temp = temp + temp

        return result

    @classmethod
    def get_valid_point(cls, curve):
        """
        Generate point where x and y are integers

        :param curve: Curve
        :return: Point
        """
        x, y = None, None
        while y is None:
            x = random.randint(1, curve.mod - 1)
            rhs = (x ** 3 + curve.a * x + curve.b) % curve.mod
            y = sqrt_mod(rhs, curve.mod)

        return cls(x, y, curve)


class ECC:
    """
    The ECC class
    """
    def create_keys(self):
        """
        Generates keys

        :return: tuple[str, str], private and public keys
        """
        curve = Curve(utils.get_prime(), utils.get_prime(), utils.get_prime())

        G = Point.get_valid_point(curve)
        p = utils.get_prime()

        P = G * p

        r = utils.get_prime()
        R = G * r
        S = P * r

        S_dec = R * p

        public_key = sha256(S.x.to_bytes(32)).digest()
        private_key = sha256(S_dec.x.to_bytes(32)).digest()

        return private_key, public_key


    def encrypt(self, key, message: bytes):
        """
        Encrypts the message with a key

        :param key: str, key to encrypt
        :param message: bytes, message to encrypt
        :return: tuple[str, int], encrypted message and IV
        """
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(utils.transform_msg(message))
        return encrypted, iv


    def decrypt(self, key, encrypted, iv):
        """
        Decrypts the message with a key

        :param key: str, key to encrypt
        :param encrypted: str, message to decrypt
        :param iv: int, IV coefficient
        :return: str
        """

        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted).decode()
        return decrypted


if __name__ == '__main__':
    ecc = ECC()
    private_key, public_key = ecc.create_keys()
    encrypted, iv = ecc.encrypt(public_key, b'Hello')
    print(ecc.decrypt(private_key, encrypted, iv))
