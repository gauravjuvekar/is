#!/usr/bin/env python3
from collections import deque
import argparse
import getpass

import pprint


def sanitize_input(string):
    string = string.upper()
    if not string.isupper():
        raise ValueError("Only alphabetic strings allowed")
    return string


def make_matrix(key):
    matrix = [[None] * 5 for _ in range(5)]
    key = sanitize_input(key)
    key += "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    key = deque(key)
    rmap = dict()
    for i in range(5):
        for j in range(5):
            c = key.popleft()
            while c in rmap:
                c = key.popleft()
            matrix[i][j] = c
            rmap[c] = (i, j)
    rmap['J'] = rmap['I']
    return matrix, rmap


def get_pairs(message):
    ret_char = ''
    for char in message:
        if ret_char == char:
            if ret_char != 'X':
                yield ret_char + 'X'
            else:
                yield ret_char + 'Y'
            ret_char = char
        else:
            ret_char += char
        if len(ret_char) == 2:
            yield ret_char
            ret_char = ''
    else:
        if len(ret_char) == 2:
            yield ret_char
            ret_char = ''
        elif len(ret_char) == 0:
            return
        else:
            if ret_char != 'X':
                yield ret_char + 'X'
            else:
                yield ret_char + 'Y'


def encrypt_generator(matrix, rmap, message_pairs):
    for pair in message_pairs:
        c0, c1 = pair
        i0, i1 = rmap[c0], rmap[c1]
        if i0[0] == i1[0]:
            yield (matrix[i0[0]][(i0[1] + 1) % 5],
                   matrix[i1[0]][(i1[1] + 1) % 5])
        elif i0[1] == i1[1]:
            yield (matrix[(i0[0] + 1) % 5][i0[1]],
                   matrix[(i1[0] + 1) % 5][i1[1]])
        else:
            yield (matrix[i0[0]][i1[1]],
                   matrix[i1[0]][i0[1]])


def decrypt_generator(matrix, rmap, message_pairs):
    for pair in message_pairs:
        c0, c1 = pair
        i0, i1 = rmap[c0], rmap[c1]
        if i0[0] == i1[0]:
            yield (matrix[i0[0]][(i0[1] - 1) % 5],
                   matrix[i1[0]][(i1[1] - 1) % 5])
        elif i0[1] == i1[1]:
            yield (matrix[(i0[0] - 1) % 5][i0[1]],
                   matrix[(i1[0] - 1) % 5][i1[1]])
        else:
            yield (matrix[i0[0]][i1[1]],
                   matrix[i1[0]][i0[1]])


def encrypt(key, message):
    matrix, rmap = make_matrix(key)
    encrypted = ''.join(
        (''.join(x)
         for x in encrypt_generator(matrix, rmap, get_pairs(message))))
    return encrypted


def decrypt(key, message):
    matrix, rmap = make_matrix(key)
    decrypted = ''.join(
        (''.join(x)
         for x in decrypt_generator(matrix, rmap, get_pairs(message))))
    return decrypted


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ACTION', choices=['encrypt', 'decrypt'])
    args = parser.parse_args()

    key = getpass.getpass("Enter key (alphabets only):").upper()
    text = input().strip('\n').replace(' ', '').upper()

    if args.ACTION == 'encrypt':
        print(encrypt(key, text))
    else:
        print(decrypt(key, text))
