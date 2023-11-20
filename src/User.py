from __future__ import annotations
import hashlib
from src.Signature import *


class User:
    def __init__(self, username: str, password: str, encoded_keys: tuple[bytes, bytes]):
        self.username = username
        self.password = self.__password_hash(password)
        self.private_key, self.public_key = encoded_keys

    def __password_hash(self, password: str) -> bytes:
        return hashlib.sha256(bytes(self.username + password, 'utf8')).digest()

    def authorize(self, password: str) -> bool:
        return self.password == self.__password_hash(password)

    def get_rsa_keys(self, password: str) -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        if self.authorize(password):
            return decode_keys((self.private_key, self.public_key), password)

    def get_public_key(self) -> rsa.RSAPublicKey:
        return decode_public_key(self.public_key)

    def __eq__(self, other: User) -> bool:
        return self.username == other.username and self.public_key == other.public_key and self.private_key == other.private_key

    def __repr__(self) -> str:
        return f"User {self.username} | Public Key: {self.public_key}"
