from binascii import hexlify, unhexlify
from Crypto.Cipher import DES
import matplotlib.pyplot as plt
import random
import timeit


def time_run(mode):
    key = bytes([random.randrange(256) for _ in range(8)])
    IV = bytes([random.randrange(256) for _ in range(8)])
    cipher = DES.new(key, mode=mode, IV=IV)
    plain_size = [8]
    timer = timeit.Timer(
        stmt='cipher.encrypt(plaintext)',
        setup="""
import random
plaintext = bytes([random.randrange(256) for _ in range(plain_size[0])])
""",
        globals=locals())

    last_time = 0
    data_points = {'x': [], 'y': []}
    while last_time < 0.005:
        last_time = timer.repeat(repeat=5, number=1)
        print(plain_size[0], last_time)
        data_points['x'].extend([plain_size[0]] * len(last_time))
        data_points['y'].extend(last_time)
        last_time = min(last_time)
        plain_size[0] += 32000
    return data_points

if __name__ == '__main__':
    fig, ax = plt.subplots()
    # plt.rc('axes', color_cycle=['r', 'g', 'b', 'y'])
    ax.set(title='DES performance (pycrypto)',
           xlabel='plaintext size',
           ylabel='time (s)')
    legends = []
    for i, mode in enumerate([(DES.MODE_ECB, 'ECB'), (DES.MODE_CBC, 'CBC'),
                              (DES.MODE_OFB, 'OFB')]):
        mode, mode_str = mode
        data_points = time_run(mode)
        legends.append(ax.scatter(data_points['x'], data_points['y'],
                                  label=mode_str, c=['r', 'g', 'b'][i]))
    plt.legend(handles=legends)
    plt.savefig('plot.png')
    plt.show()
