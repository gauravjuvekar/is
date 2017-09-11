#!/usr/bin/env python3
import argparse
import getpass
import numpy as np


def sanitize_input(string):
    string = string.upper()
    if not string.isupper():
        raise ValueError("Only alphabetic strings allowed")
    return string


def generate_inv_table(mod):
    inv = [None] * mod
    for i in range(mod):
        if inv[i] is None:
            for j in range(mod):
                if ((i * j) % mod) == 1:
                    inv[i] = j
                    inv[j] = i
    return inv


def matrix_mod_inv(A, mod, inv_table):
    n = len(A)
    A = np.matrix(A, dtype=int)
    adj = np.zeros(shape=(n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            adj[i][j] = (
                (-1)**(i + j) *
                int(round(np.linalg.det(minor(A, j, i))))) % mod
    print(A)
    print(adj)
    print(inv_table)
    det_inv = int(round(np.linalg.det(A))) % mod
    print(det_inv)
    if inv_table[det_inv] is None:
        raise ValueError("Determinant is not invertible")
    else:
        return (inv_table[det_inv] * adj) % mod


def minor(A, i, j):
    A = np.array(A, dtype=int)
    minor = np.zeros(shape=(len(A)-1, len(A)-1), dtype=int)
    p = 0
    for s in range(0, len(minor)):
        if p == i:
            p += 1
        q = 0
        for t in range(0, len(minor)):
            if q == j:
                q += 1
            minor[s][t] = A[p][q]
            q += 1
        p += 1
    return minor


def encrypt_block(matrix, plaintext):
    cipher_text = ''
    length = len(matrix)
    plaintext = np.array([ord(c) - ord('A') for c in plaintext], dtype=int)
    for count, c in enumerate(plaintext):
        cipher_text += (
            chr(sum(matrix[count % length] * plaintext) % 26 + ord('A')))
    return cipher_text


def decrypt_block(matrix, ciphertext):
    plain_text = ''
    length = len(matrix)
    ciphertext = np.array([ord(c) - ord('A') for c in ciphertext], dtype=int)
    for i, c in enumerate(ciphertext):
        number = sum(matrix[i % length] * ciphertext) % 26
        plain_text += chr(ord('A') + int(number))
    return plain_text


def encrypt(key, message):
    mat_n, key = check_key(key)

    if len(message) % mat_n:
        message += 'X' * (len(message) % mat_n)

    ciphertext = ''
    for i in range((len(message) // mat_n)):
        ciphertext += encrypt_block(key, message[i * mat_n:(i + 1) * mat_n])
    return ciphertext


def check_key(key):
    mat_n = int(len(key)**0.5 + 0.5)
    if not (mat_n**2 == len(key)):
        raise ValueError("Key must be a perfect square in length")

    key = np.array([ord(c) - ord('A') for c in key], dtype=int)
    key = key.reshape((mat_n, mat_n))
    try:
        inv_key = matrix_mod_inv(key, 26, generate_inv_table(26))
    except np.linalg.LinAlgError:
        raise ValueError("Key must be invertible")

    return mat_n, key


def decrypt(key, message):
    mat_n, key = check_key(key)

    inv_key = matrix_mod_inv(key, 26, generate_inv_table(26))

    if len(message) % mat_n:
        raise ValueError("Message must be a multiple of sqrt(key) size")

    plaintext = ''
    for i in range((len(message) // mat_n)):
        plaintext += decrypt_block(inv_key, message[i * mat_n:(i + 1) * mat_n])
    return plaintext


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ACTION', choices=['encrypt', 'decrypt'])
    args = parser.parse_args()

    key = sanitize_input(
        getpass.getpass("Enter key (alphabets only):").upper())
    text = sanitize_input(input().strip('\n').replace(' ', '').upper())

    if args.ACTION == 'encrypt':
        print(encrypt(key, text))
    else:
        print(decrypt(key, text))
