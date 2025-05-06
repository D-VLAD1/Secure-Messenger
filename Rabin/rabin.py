'''Rabin's algorithm for public key cryptography'''''
import random

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
def generate_keys():
    # Ensure p ≡ q ≡ 3 mod 4
    p = q = 4
    while not (miller_rabin(p) and p % 4 == 3):
        p = random.randint(10**50, 10**60)
    while not (miller_rabin(q) and q % 4 == 3) or q == p:
        q = random.randint(10**50, 10**60)
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
print("Decryption successful!")
