#!/usr/bin/env python3
from collections import deque
import argparse
import getpass


def sanitize_input(string):
    string = string.upper()
    if not string.isupper():
        raise ValueError("Only alphabetic strings allowed")
    return string


def encrypt_value(k, p):
    return chr(ord('A') + (((ord(k) - ord('A')) + (ord(p) - ord('A'))) % 26))


def encrypt_generator(key, plaintext):
    d = deque()
    d.extend(list(key))
    for p in plaintext:
        d.append(p)
        yield encrypt_value(d.popleft(), p)


def encrypt(key, plaintext):
    key = sanitize_input(key)
    plaintext = sanitize_input(plaintext)
    return ''.join(encrypt_generator(key, plaintext))


def decrypt_value(k, c):
    return chr(ord('A') + (((ord(c) - ord('A') + 26) -
                            (ord(k) - ord('A'))) % 26))


def decrypt_generator(key, ciphertext):
    d = deque()
    d.extend(list(key))
    for c in ciphertext:
        p = decrypt_value(d.popleft(), c)
        d.append(p)
        yield p


def decrypt(key, ciphertext):
    key = sanitize_input(key)
    ciphertext = sanitize_input(ciphertext)
    return ''.join(decrypt_generator(key, ciphertext))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ACTION', choices=['encrypt', 'decrypt'])
    args = parser.parse_args()

    key = getpass.getpass("Enter key (alphabets only):")
    text = input().strip('\n').replace(' ', '')

    if args.ACTION == 'encrypt':
        print(encrypt(key, text))
    else:
        print(decrypt(key, text))
