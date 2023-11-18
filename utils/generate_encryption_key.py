from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from environs import Env

env = Env()
env.read_env()

PASSWORD = env('PASSWORD_FOR_ENCRYPTION')
dkLen = env.int('dkLen')


def generate_key():
    return PBKDF2(PASSWORD, get_random_bytes(32), dkLen=dkLen)


if __name__ == '__main__':
    print(generate_key())
