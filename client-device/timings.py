import util
import os
import keys


def time_hash(n):
    data = os.urandom(256)
    for i in range(n):
        with util.Timer('time_hash'):
            util.hash(data)


def time_ecies(n):
    ct = list()
    for i in range(n):
        data = os.urandom(256)
        with util.Timer('time_ecies_encryption'):
            c = util.ecies_encryption(keys.public_key(), data)
        ct.append(c)
    for c in ct:
        with util.Timer('time_ecies_decryption'):
            p = util.ecies_decryption(keys.private_key(), c)


def time_aes(n):
    key = os.urandom(32)
    nonce = os.urandom(12)
    ct = list()
    for i in range(n):
        data = os.urandom(256)
        with util.Timer('time_aes_encryption'):
            c = util.encrypt(key, nonce, data)
        ct.append(c)
    for c in ct:
        with util.Timer('time_aes_decryption'):
            p = util.decrypt(key, nonce, c)


if __name__ == '__main__':
    time_hash(1000)
    time_ecies(1000)
    time_aes(1000)

    util.Timer.record_timings('time_hash')
    util.Timer.record_timings('time_ecies_encryption')
    util.Timer.record_timings('time_ecies_decryption')
    util.Timer.record_timings('time_aes_encryption')
    util.Timer.record_timings('time_aes_decryption')
    # with open('temp/timings.csv', 'w') as file:
    #     util.Timer.record_timings('time_hash', file=file)
    #     util.Timer.record_timings('time_ecies_encryption', file=file)
