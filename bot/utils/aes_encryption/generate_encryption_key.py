import base64

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes


def generate_key(password: str, dklen: int, iterations: int) -> bytes:
    """Сгенерировать ключ шифрования."""
    bytes_key = PBKDF2(
        password=password,
        salt=get_random_bytes(dklen),
        dkLen=dklen,
        count=iterations
    )
    return base64.b64encode(bytes_key)


if __name__ == '__main__':
    from environs import Env

    env = Env()
    env.read_env()

    PASSWORD = env('PASSWORD_FOR_ENCRYPTION')
    DKLEN = env.int('DKLEN')
    ITERATIONS = env.int('ITERATIONS_FOR_ENCRYPTION')

    print(
        generate_key(
            password=PASSWORD,
            dklen=DKLEN,
            iterations=ITERATIONS
        )
    )
