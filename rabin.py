import random
import math

def is_prime(n):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_keys():
    # Ensure p ≡ q ≡ 3 mod 4
    p = q = 4
    while not (is_prime(p) and p % 4 == 3):
        p = random.randint(2**5, 2**6)
    while not (is_prime(q) and q % 4 == 3) or q == p:
        q = random.randint(2**5, 2**6)
    n = p * q
    return (n, p, q)

def encrypt(m, n):
    return pow(m, 2, n)

def decrypt(c, p, q):
    n = p * q
    # Handle case where c is not a quadratic residue
    if pow(c, (p-1)//2, p) != 1 or pow(c, (q-1)//2, q) != 1:
        return None
    
    # Compute square roots mod p and q
    mp = pow(c, (p + 1) // 4, p)
    mq = pow(c, (q + 1) // 4, q)
    
    # Apply Chinese Remainder Theorem
    def crt(a, b):
        return (a * q * pow(q, -1, p) + b * p * pow(p, -1, q)) % n
    
    r1 = crt(mp, mq)
    r2 = crt(mp, -mq % q)
    r3 = crt(-mp % p, mq)
    r4 = crt(-mp % p, -mq % q)
    
    # Return unique roots
    return tuple(sorted({r1, r2, r3, r4}))

# Example usage
n, p, q = generate_keys()
print(f"Generated keys: n={n}, p={p}, q={q}")

message = 42
assert message < n, "Message must be smaller than n!"

ciphertext = encrypt(message, n)
print(f"Ciphertext: {ciphertext}")

decrypted = decrypt(ciphertext, p, q)
print(f"Decrypted roots: {decrypted}")

# Verify one of the roots matches original message
assert message in decrypted, "Decryption failed!"