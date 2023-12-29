import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from config_data import main_config


class AESEncryption:

    __KEY = base64.b64decode(main_config.encryption.ENCRYPTION_KEY)

    @classmethod
    def encrypt_keys(
            cls,
            decrypt: bool = False,
            **kwargs: dict[str: bytes] | dict[str: str]
    ) -> dict[str: bytes] | dict[str: str]:
        """
        Зашифровать / расшифровать API ключи.
        Шифрует если decrypt = False
        """
        cls.__check_keys(keys=kwargs, decrypt=decrypt)
        for key, value in kwargs.items():
            value = cls.decrypt(value) if decrypt else cls.encrypt(value)
            kwargs[key] = value
        return kwargs

    @classmethod
    def __check_keys(cls, keys: dict, decrypt: bool):
        if not isinstance(keys, dict):
            raise TypeError('Wrong keys type')
        if not keys:
            raise ValueError('No values to process')
        if decrypt:
            for key, value in keys.items():
                if not isinstance(key, str) or not isinstance(value, bytes):
                    raise TypeError('Wrong key or value type')
        elif not decrypt:
            for key, value in keys.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise TypeError('Wrong key or value type')

    @classmethod
    def encrypt(cls, token):
        """Шифрование токена."""
        cipher = AES.new(cls.__KEY, AES.MODE_CBC)
        cipher_data = cipher.encrypt(pad(token.encode(), AES.block_size))
        return cipher.iv + cipher_data

    @classmethod
    def decrypt(cls, encrypted_token):
        """Расшифровка токена."""
        iv = encrypted_token[:16]
        cipher = AES.new(cls.__KEY, AES.MODE_CBC, iv=iv)
        orig = unpad(cipher.decrypt(encrypted_token[16:]), AES.block_size)
        return orig.decode()
