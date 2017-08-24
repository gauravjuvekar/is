#!/usr/bin/env python3
import argparse
import binascii
import getpass
import io
import functools
import random

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BLOCK_SIZE = 32


class DecrpytionError(BaseException):
    pass


def xor(*args):
    return bytes([functools.reduce(lambda a, b: a ^ b, t) for t in zip(*args)])


def reduce_key(key):
    key = bytes(key)
    if len(key) > BLOCK_SIZE:
        for start in range(BLOCK_SIZE, len(key), BLOCK_SIZE):
            key = xor(key[:BLOCK_SIZE], key[start:start + BLOCK_SIZE])
        key = key[:BLOCK_SIZE]
    else:
        while len(key) < BLOCK_SIZE:
            key = key + key
        key = key[:BLOCK_SIZE]
    log.debug("Key is %s", binascii.hexlify(key))
    return key


def get_seed(size=BLOCK_SIZE):
    seed = [random.randrange(256) for x in range(BLOCK_SIZE)]
    seed = bytes(seed)
    return seed


def encrypt(infile, outfile, key):
    seed = get_seed(BLOCK_SIZE)
    outfile.write(seed)
    assert len(seed) == BLOCK_SIZE
    last_cipher_block = seed
    infile_len = 0
    last_block = False
    while not last_block:
        plain_block = infile.read(BLOCK_SIZE)
        infile_len += len(plain_block)
        if len(plain_block) < BLOCK_SIZE:
            last_block = True
            plain_block += bytes([0] * (BLOCK_SIZE - len(plain_block)))
        cipher_block = xor(key, last_cipher_block, plain_block)
        outfile.write(cipher_block)
        last_cipher_block = cipher_block
    log.debug("File length is %d", infile_len)
    outfile.write(infile_len.to_bytes(8, 'little'))


def decrypt(infile, outfile, key):
    last_cipher_block = infile.read(BLOCK_SIZE)
    if len(last_cipher_block) != BLOCK_SIZE:
        raise DecrpytionError("File smaller than seed block")

    last_block = False
    plain_file_size = 0
    deferred_write = bytes(b'')
    while True:
        cipher_block = infile.read(BLOCK_SIZE)
        if len(cipher_block) < BLOCK_SIZE:
            if len(cipher_block) == 8:
                expected_file_size = int.from_bytes(cipher_block, 'little')
                log.debug("Expected file length is %d", expected_file_size)
                log.debug("%d bytes decrypted till now", plain_file_size)
                if not (plain_file_size <=
                        expected_file_size <=
                        (plain_file_size + BLOCK_SIZE)):
                    raise DecrpytionError("Length error in input file")
                last_block_length = expected_file_size - plain_file_size
                if last_block_length < BLOCK_SIZE:
                    deferred_write = deferred_write[:last_block_length]
                    last_block = True
                else:
                    raise DecrpytionError("Expected file size too small")
            else:
                raise DecrpytionError("Filesize not found at tail of file")
        outfile.write(deferred_write)
        plain_file_size += len(deferred_write)
        if last_block:
            break

        plain_block = xor(cipher_block, key, last_cipher_block)
        last_cipher_block = cipher_block
        deferred_write = plain_block


def encrypt_bytes(in_bytes, key):
    in_file = io.BytesIO(in_bytes)
    out_file = io.BytesIO()
    encrypt(in_file, out_file, key)
    out_file.seek(io.SEEK_SET)
    return out_file.read()


def decrypt_bytes(in_bytes, key):
    in_file = io.BytesIO(in_bytes)
    out_file = io.BytesIO()
    decrypt(in_file, out_file, key)
    out_file.seek(io.SEEK_SET)
    return out_file.read()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ACTION', choices=['encrypt', 'decrypt'])
    parser.add_argument('INFILE', type=argparse.FileType(mode='rb'))
    parser.add_argument('OUTFILE', type=argparse.FileType(mode='wb'))
    args = parser.parse_args()

    key = getpass.getpass("Enter key:")
    key = reduce_key(key.encode())
    if args.ACTION == 'encrypt':
        encrypt(args.INFILE, args.OUTFILE, key)
    else:
        decrypt(args.INFILE, args.OUTFILE, key)
