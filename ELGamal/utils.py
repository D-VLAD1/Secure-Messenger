"""helper"""
import random
import math
from sympy import primitive_root

def generate_prime(min_value, max_value) -> int:
    """Generates a random prime number in given range"""
    prime = random.randint(min_value, max_value)
    while not miller_rabin(prime):
        prime += 1
    return prime

def create_keys():
    """Creates public and private keys for a client"""
    p = generate_prime(10**50, 10**51)
    g = primitive_root(p)
    secret_a = random.randint(2, p-2)
    e = pow(g, secret_a, p)
    return p, g, e, secret_a

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


def encode_message(message, p, g, e):
    """
    Encodes a message using Elgamal block encryption.
    Returns coded blocks as ([(c1, c2), (c1, c2), ...], last_block_len)
    """
    print(f"Encoding: {message}")
    numeric_string = ''.join(f"{ord(c):03d}" for c in message)
    print(f"Numeric string: {numeric_string}")
    block_len = len(str(p))-1
    blocks = [numeric_string[i:i+block_len] for i in range(0, len(numeric_string), block_len)]
    last_block_len = len(blocks[-1])
    print(f"Blocks: {blocks}")
    k = random.randint(2, p-2)
    # [(c1, c2), (c1, c2), (c1, c2), ...]
    encrypted_blocks = [(pow(g, k, p), pow(int(block)*pow(e, k, p), 1, p)) for block in blocks]
    return encrypted_blocks, last_block_len

def decode_message(encrypted_blocks, last_block_len, p, a):
    """
    Decodes a message using Elgamal block encryption.
    Returns coded blocks as ([(c1, c2), (c1, c2), ...], last_block_len)
    """
    decrypted_blocks = []
    for i, block in enumerate(encrypted_blocks):
        c1, c2 = block
        s = pow(c1, a, p)
        decrypted_block = str(pow(c2*pow(s, p - 2, p), 1, p))
        print(f"Decrypted block: {decrypted_block}")
        if i != len(encrypted_blocks)-1:
            decrypted_block = decrypted_block.zfill(len(str(p))-1)
        else:
            decrypted_block = decrypted_block.zfill(last_block_len)
        print(f"Decrypted filled block: {decrypted_block}")
        decrypted_blocks.append(decrypted_block)

    numeric_string = "".join(decrypted_blocks)
    print(f"Numeric string: {numeric_string}")
    decoded_message = ''.join(chr(int(numeric_string[i:i+3])) for i in range(0, len(numeric_string), 3))
    return decoded_message

