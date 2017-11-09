from binascii import hexlify, unhexlify
from Crypto.Cipher import AES


for key, plain in [
            ('00' * 16, '00' * 16),
            ('ff' * 16, 'ff' * 16),
            ('ff' * 16, '00' * 16),
            ('00' * 15 + '01', '00' * 16),
            ('00' * 16, '00' * 15 + '01'),
            ('00' * 15 + '02', '00' * 16),
            ('00' * 15 + '03', '00' * 16),
            ('80' + '00' * 15, '00' * 16),
            ('00' * 8 + 'ff' * 8, '00' * 16),
            ('00' * 15 + '01', '00' * 15 + '01'),
        ]:
    key = unhexlify(key)
    plain = unhexlify(plain)
    encryptor = AES.new(key=key)
    print("Key       :", hexlify(key))
    print("Plaintext :", hexlify(plain))
    print("Ciphertext:", hexlify(encryptor.encrypt(plain)))
    print('-' * 31)
