"""Computes a average time for each algorithm to compute its keys"""
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import RSA.utils
import Elgamal.utils
import Rabin.rabin

def key_gen_time_rsa(min_val, max_val, iterations):
    """Returns an average time to generate RSA keys"""
    result = []
    print("RSA keys are generating...")
    for _ in range(iterations):
        start_time = time.time()
        p = RSA.utils.get_key(min_val, max_val)  # p generation
        q = RSA.utils.get_key(min_val, max_val)  # q generation
        mod = p * q
        phi = (p - 1) * (q - 1)
        e = RSA.utils.generate_key(phi) # public e
        d = pow(e, -1, phi) # private d

        one_iter_time = time.time() - start_time
        result.append(one_iter_time)
    print("RSA keys are done!")
    average_time = sum(result)/len(result)
    return average_time


def key_gen_time_elgamal(min_val, max_val, iterations):
    """Returns an average time to generate Elgamal keys"""
    result = []
    print("Elgamal keys are generating...")
    for _ in range(iterations):
        start_time = time.time()
        p = Elgamal.utils.generate_prime(min_val, max_val) # prime p
        g = Elgamal.utils.primitive_root(p) # primitive root g
        secret_a = Elgamal.utils.random.randint(2, p-2) # a
        e = pow(g, secret_a, p) # e
        one_iter_time = time.time() - start_time
        result.append(one_iter_time)
        print(f"Iteration: {_}")
    print("Elgamal keys are done!")
    average_time = sum(result)/len(result)
    return average_time

def key_gen_time_rabin(min_val, max_val, iterations):
    """Returns an average time to generate Rabin keys"""
    result = []
    print("Rabin keys are generating...")
    for _ in range(iterations):
        start_time = time.time()
        n, p, q = Rabin.rabin.generate_keys(min_val, max_val) # n-public p, q-private
        one_iter_time = time.time() - start_time
        result.append(one_iter_time)
    print("Rabin keys are done!")
    average_time = sum(result)/len(result)
    return average_time

def key_gen_time_ecc(min_val, max_val, iterations):
    """Returns an average time to generate ECC keys"""
    result = []
    print("ECC keys are generating...")
    for _ in range(iterations):
        start_time = time.time()
        curve = ECC.client.Curve(ECC.utils.get_prime(), ECC.utils.get_prime(), ECC.utils.get_prime())
        one_iter_time = time.time() - start_time
        result.append(one_iter_time)
    print("ECC keys are done!")
    average_time = sum(result)/len(result)
    return average_time

if __name__ == "__main__":
    min_value, max_value = 10**50, 10**51
    iters = 100
    # rabin_time = key_gen_time_rabin(min_value, max_value, iters)
    # print(rabin_time)
    # rsa_time = key_gen_time_rsa(min_value, max_value, iters)
    # print(rsa_time)
    elg_time = key_gen_time_elgamal(min_value, max_value, iters)
    print(elg_time)
