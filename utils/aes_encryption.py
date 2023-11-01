import ast

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from environs import Env

env = Env()
env.read_env()


class AESEncryption:

    __key = ast.literal_eval(env('ENCRYPTION_KEY'))

    @classmethod
    def encrypt(cls, token):
        """Шифрование токена."""
        cipher = AES.new(cls.__key, AES.MODE_CBC)
        cipher_data = cipher.encrypt(pad(token.encode(), AES.block_size))
        return cipher.iv + cipher_data

    @classmethod
    def decrypt(cls, encrypted_token):
        """Расшифровка токена."""
        iv = encrypted_token[:16]
        cipher = AES.new(cls.__key, AES.MODE_CBC, iv=iv)
        orig = unpad(cipher.decrypt(encrypted_token[16:]), AES.block_size)
        return orig.decode()
