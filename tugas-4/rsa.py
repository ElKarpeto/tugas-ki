from math import gcd
from sympy import randprime
import hashlib


class RSA:
    def Hex2Int(self, s: str) -> int:
        return int(s, 16)

    def Int2hex(self, n: int) -> str:
        return hex(n)[2:]

    def modInverse(self, e: int, phi: int) -> int:
        d = pow(e, -1, phi)
        while d < 0:
            d += phi
        return d

    def generateKeys(self) -> tuple[int, int, int]:
        p = randprime(1_000_000_000_000_000, 9_999_999_999_999_999)
        q = randprime(1_000_000_000_000_000, 9_999_999_999_999_999)

        n = p * q
        phi = (p - 1) * (q - 1)

        e = 0
        for i in range(2, phi):
            if gcd(i, phi) == 1:
                e = i
                break

        d = self.modInverse(e, phi)
        return e, d, n

    def encrypt(self, msg: int, e: int, n: int) -> int:
        return pow(msg, e, n)

    def decrypt(self, cipher: int, d: int, n: int) -> int:
        return pow(cipher, d, n)

    # NEW: hash → integer
    def sha256_int(self, text: str) -> int:
        h = hashlib.sha256(text.encode()).hexdigest()
        return int(h, 16)
