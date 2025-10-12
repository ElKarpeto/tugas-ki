INITIAL_PERM = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

PC1_TABLE = [
    57, 49, 41, 33, 25, 17, 9, 1,
    58, 50, 42, 34, 26, 18, 10, 2,
    59, 51, 43, 35, 27, 19, 11, 3,
    60, 52, 44, 36, 63, 55, 47, 39,
    31, 23, 15, 7, 62, 54, 46, 38,
    30, 22, 14, 6, 61, 53, 45, 37,
    29, 21, 13, 5, 28, 20, 12, 4
]

PC2_TABLE = [
    14, 17, 11, 24, 1, 5, 3, 28,
    15, 6, 21, 10, 23, 19, 12, 4,
    26, 8, 16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55, 30, 40,
    51, 45, 33, 48, 44, 49, 39, 56,
    34, 53, 46, 42, 50, 36, 29, 32
]

SHIFT_TABLE = [
    1, 1, 2, 2, 
    2, 2, 2, 2, 
    1, 2, 2, 2, 
    2, 2, 2, 1
]

EXP_PERM = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

S_BOXES = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]

P_BOX = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
]

INVERSE_TABLE = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

def Hex2Binary(s : str) -> str :
    res = bin(int(s, 16))[2:]
    res = '0' * (4 * len(s) - len(res)) + res
    return res

def Binary2Hex(s : str) -> str :
    res = hex(int(s, 2))[2:]
    res = '0' * (len(s) // 4 - len(res)) + res
    return res

def String2Binary(s : str) -> str :
    res = ''.join(format(ord(c), '08b') for c in s)
    return res

def Binary2String(s : str) -> str :
    res = ''.join(chr(int(s[i:i+8], 2)) for i in range(0, len(s), 8))
    return res

def printBinary(s : str) -> str :
    return ' '.join(s[i:i+4] for i in range(0, len(s), 4))

def Dec2Binary(x : int, n : int) -> str :
    res = bin(x)[2:]
    res = '0' * (n - len(res)) + res
    return res

def generateKey() -> str :
    import random
    random.seed(19)

    key = ''.join(random.choice('0123456789ABCDEF') for _ in range(16))
    return key

def permute(s : str, table : list[int], n : int) -> str :
    res = ""
    for i in range(n) :
        res += s[table[i] - 1]
    
    return res

def shift_left(s : str, k : int) -> str :
    res = ""
    for i in range(len(s)) :
        res += s[(i + k) % len(s)]
    
    return res

def generateRoundKey(left_key : str, right_key : str, n : int) -> tuple[str, str, str] :
    left_key = shift_left(left_key, SHIFT_TABLE[n])
    right_key = shift_left(right_key, SHIFT_TABLE[n])
    round_key = permute(left_key + right_key, PC2_TABLE, 48)

    return left_key, right_key, round_key

def XOR(a : str, b : str) -> str :
    res = ""
    for i in range(len(a)) :
        res += '1' if a[i] != b[i] else '0'
    
    return res

def F(left : str, right : str, round_key : str) -> tuple[str, str] :
    right_exp = permute(right, EXP_PERM, 48)

    xor_res = XOR(right_exp, round_key)

    sbox_res = ""
    for i in range(8) :
        row = int(xor_res[i*6] + xor_res[i*6 + 5], 2)
        col = int(xor_res[i*6 + 1:i*6 + 5], 2)
        sbox_val = S_BOXES[i][row][col]
        sbox_res += Dec2Binary(sbox_val, 4)

    pbox_res = permute(sbox_res, P_BOX, 32)
    
    f_res = XOR(left, pbox_res)
    left = right
    right = f_res

    return left, right

while True :
    key = generateKey()
    print(f"Initial Key: {key}")

    key = Hex2Binary(key)
    print(f"Binary Key: {printBinary(key)}\n")
    key = permute(key, PC1_TABLE, 56)

    left_key = key[:28]
    right_key = key[28:]

    mode = input("Format Input (hex/text): ").strip().lower()
    match mode :
        case 'hex' :
            plaintext = input("Enter Plaintext (16 hex digits): ").strip()
            if len(plaintext) != 16 or any(c not in '0123456789abcdefABCDEF' for c in plaintext) :
                print("Invalid Plaintext\n")
                break
            plaintext = Hex2Binary(plaintext)
            print(f"Binary Plaintext: {printBinary(plaintext)}\n")

            output_format = 'hex'
        case 'text' :
            plaintext = input("Enter Plaintext (8 characters): ")
            if len(plaintext) != 8 :
                print("Invalid Plaintext\n")
                break
            plaintext = String2Binary(plaintext)
            print(f"Binary Plaintext: {printBinary(plaintext)}\n")
            output_format = 'text'
        case _ :
            print("Invalid Format\n")
            break

    text = permute(plaintext, INITIAL_PERM, 64)
    left = text[:32]
    right = text[32:]

    round_keys = []
    print("Encryption:")
    for i in range(16) :
        print(f"Round {i + 1}:")

        left_key, right_key, round_key = generateRoundKey(left_key, right_key, i)
        round_keys.append(round_key)
        left, right = F(left, right, round_key)

        print(f"Left (R{i + 1}): {printBinary(left)}")
        print(f"Right (R{i + 1}): {printBinary(right)}")
        print(f"Key: {printBinary(left_key + right_key)}\n")
        
    left, right = right, left
    cipher = permute(left + right, INVERSE_TABLE, 64)

    print(f"Binary Ciphertext: {printBinary(cipher)}")
    print(f"Ciphertext: {Binary2Hex(cipher).upper() if output_format == 'hex' else Binary2String(cipher)}\n")

    print("Decryption:")
    for i in range(16) :
        print(f"Round {16 - i}:")
        left, right = F(left, right, round_keys[15 - i])
        print(f"Left (R{16 - i}): {printBinary(left)}")
        print(f"Right (R{16 - i}): {printBinary(right)}\n")

    plain = permute(right + left, INVERSE_TABLE, 64)
    print(f"Plaintext: {Binary2Hex(plain).upper() if output_format == 'hex' else Binary2String(plain)}\n")

    cont = input("Continue? (y/n): ").strip().lower()
    match cont :
        case 'y' :
            print()
            continue
        case 'n' :
            break
        case _ :
            print("Invalid Input")
            break