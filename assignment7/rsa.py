from binascii import hexlify, unhexlify
from Crypto.PublicKey import RSA
import matplotlib.pyplot as plt
import random
import timeit

def time_run(keysize):
    rsa_key_pair = RSA.generate(keysize)
    pub_key = rsa_key_pair.publickey()

    timer = timeit.Timer(
        stmt='pub_key.encrypt(plaintext, K=0)',
        setup="""
import random
plaintext = bytes([random.randrange(256)
                   for _ in range((pub_key.n.bit_length() - 1) // 8)])
""",
        globals=locals())

    last_time = 0
    number = 10
    data_points = {'x': [], 'y': []}
    while last_time < 0.5:
        last_time = timer.repeat(repeat=5, number=number)
        print(number, last_time)
        data_points['x'].extend([number] * len(last_time))
        data_points['y'].extend(last_time)
        last_time = min(last_time)
        number += 100
    return data_points

if __name__ == '__main__':
    fig, ax = plt.subplots()
    # plt.rc('axes', color_cycle=['r', 'g', 'b', 'y'])
    ax.set(title='RSA performance (pycrypto)',
           xlabel='iterations',
           ylabel='time (s)')
    legends = []
    for i, keysize in enumerate((1024, 2048, 4096)):
        data_points = time_run(keysize)
        legends.append(ax.scatter(data_points['x'], data_points['y'],
                                  label=str(keysize), c=['r', 'g', 'b'][i]))
    plt.legend(handles=legends)
    plt.savefig('plot.png')
    plt.show()
