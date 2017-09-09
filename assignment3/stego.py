#!/usr/bin/env python3
import argparse
import PIL
import PIL.Image
import sys


def bit_reader(stream):
    while True:
        byte = stream.read(1)
        if not(len(byte)):
            break
        byte = ord(byte)
        for idx in range(8):
            yield (byte & (1 << (7 - idx))) >> (7 - idx)


def byte_to_bits(byte_iter):
    for byte in byte_iter:
        for idx in range(8):
            yield (byte & (1 << (7 - idx))) >> (7 - idx)


def encode(args):
    image = PIL.Image.open(args.INPUT_IMAGE)
    image = image.convert('RGB')
    image = image.copy()
    bits = bit_reader(args.INPUT_TEXT)
    count = 0
    try:
        for i in range(1, image.size[0]):
            for j in range(image.size[1]):
                pixel = image.getpixel((i, j))
                pixel = list(pixel)
                for color in range(len(pixel)):
                    try:
                        pixel[color] = (pixel[color] & 0xfe) | next(bits)
                        count += 1
                    except StopIteration:
                        image.putpixel((i, j), tuple(pixel))
                        raise
                image.putpixel((i, j), tuple(pixel))
    except StopIteration:
        pass
    print("Encoded", count, "bits", file=sys.stderr)
    count = iter(byte_to_bits(count.to_bytes(4, 'little')))
    try:
        i = 0
        for j in range(image.size[1]):
            pixel = image.getpixel((i, j))
            pixel = list(pixel)
            for color in range(len(pixel)):
                try:
                    pixel[color] = (pixel[color] & 0xfe) | next(count)
                except StopIteration:
                    image.putpixel((i, j), tuple(pixel))
                    raise
            image.putpixel((i, j), tuple(pixel))
    except StopIteration:
        pass
    image.save(args.OUTPUT_IMAGE.name)


def iter_image_lsbs(image, i_start=0, j_start=0):
    for i in range(i_start, image.size[0]):
        for j in range(j_start, image.size[1]):
            pixel = image.getpixel((i, j))
            pixel = list(pixel)
            for color in pixel:
                yield color & 1


def decode(args):
    image = PIL.Image.open(args.INPUT_IMAGE)
    image = image.convert('RGB')
    image = image.copy()
    iter_bits = iter_image_lsbs(image, i_start=0)
    length_bytes = [0, 0, 0, 0]
    for i in range(4):
        for j in range(8):
            bit = next(iter_bits)
            length_bytes[i] = (length_bytes[i] << 1) | bit
    assert any(length_bytes)
    length = int.from_bytes(bytes(length_bytes), 'little')

    iter_bits = iter_image_lsbs(image, i_start=1)
    this_byte = 0
    this_bit_count = 0
    for bit in range(length):
        bit = next(iter_bits)
        this_byte = (this_byte << 1) | bit
        this_bit_count += 1
        if this_bit_count == 8:
            this_bit_count = 0
            args.OUTPUT_TEXT.write(this_byte.to_bytes(1, 'little'))
            this_byte = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    encoder = subparsers.add_parser("encode")
    encoder.add_argument("INPUT_TEXT", type=argparse.FileType('rb'))
    encoder.add_argument("INPUT_IMAGE", type=argparse.FileType('rb'))
    encoder.add_argument("OUTPUT_IMAGE", type=argparse.FileType('wb'))
    encoder.set_defaults(func=encode)
    decoder = subparsers.add_parser("decode")
    decoder.add_argument("INPUT_IMAGE", type=argparse.FileType('rb'))
    decoder.add_argument("OUTPUT_TEXT", type=argparse.FileType('wb'))
    decoder.set_defaults(func=decode)
    args = parser.parse_args()
    args.func(args)
