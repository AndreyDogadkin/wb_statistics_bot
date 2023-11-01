import ast

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from environs import Env

env = Env()
env.read_env()


class AESEncryption:

    def __init__(self, key: bytes = (ast.literal_eval(env('ENCRYPTION_KEY')))):  # TODO Найти другой способ получения ключа
        self.__key = key

    def encrypt(self, token):
        cipher = AES.new(self.__key, AES.MODE_CBC)
        cipher_data = cipher.encrypt(pad(token.encode(), AES.block_size))
        return cipher.iv + cipher_data

    def decrypt(self, encrypted_token):
        iv = encrypted_token[:16]
        cipher = AES.new(self.__key, AES.MODE_CBC, iv=iv)
        orig = unpad(cipher.decrypt(encrypted_token[16:]), AES.block_size)
        return orig.decode()
