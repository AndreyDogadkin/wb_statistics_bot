import base64

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from environs import Env

env = Env()
env.read_env()

PASSWORD = env('PASSWORD_FOR_ENCRYPTION')
DKLEN = env.int('DKLEN')


def generate_key():
    """Сгенерировать ключ шифрования."""
    bytes_key = PBKDF2(PASSWORD, get_random_bytes(32), dkLen=DKLEN)
    return base64.b64encode(bytes_key)


if __name__ == '__main__':
    print(generate_key())
