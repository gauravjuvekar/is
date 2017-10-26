from binascii import hexlify, unhexlify
from Crypto.Cipher import DES


for key, plain in [
            ('00' * 8, '00' * 8),
            ('00' * 7 + '01', '00' * 8),
            ('00' * 7 + '02', '00' * 8),
            ('00' * 7 + '03', '00' * 8),
            ('80' + '00' * 7, '00' * 8),
            ('80' + '00' * 6 + '01', '00' * 8),
            ('00' * 4 + 'ff' * 4, '00' * 8),
            ('00' * 8, '00' * 7 + '01'),
            ('00' * 7 + '01', '00' * 7 + '01'),
            ('00' * 4 + '80' + '00' * 3, '00' * 7 + '01'),
            ('0E329232EA6D0D73', '87' * 8),     # Taken from the internet
        ]:
    key = unhexlify(key)
    plain = unhexlify(plain)
    encryptor = DES.new(key=key)
    print("Key       :", hexlify(key))
    print("Plaintext :", hexlify(plain))
    print("Ciphertext:", hexlify(encryptor.encrypt(plain)))
    print('-' * 31)
