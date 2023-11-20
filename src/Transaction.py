from __future__ import annotations
from math import fsum, isclose
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from src.Signature import *

REWARD_VALUE = 50.0
NORMAL = 0
REWARD = 1


class Tx:
    def __init__(self, input: float, output: float, fee: float, sender: rsa.RSAPublicKey, receiver: rsa.RSAPublicKey, type=NORMAL):
        self.type = type
        self.sender = encode_public_key(sender)
        self.receiver = encode_public_key(receiver)
        self.input = input
        self.output = output
        self.fee = fee
        self.sig = None
        self.hash = None
        self.created_at = datetime.now().strftime(r'%m/%d/%Y %I:%M:%S.%f')

    def sign(self, private: rsa.RSAPrivateKey):
        self.hash = self.compute_hash()
        self.sig = sign(self.hash, private)

    def hash_is_valid(self) -> bool:
        return self.hash is None or self.hash == self.compute_hash()

    def signed_by(self, pub_key: bytes) -> bool:
        return self.sig is not None and verify(self.hash, self.sig, decode_public_key(pub_key))

    def sent_by(self, sender_addr: bytes) -> bool:
        return sender_addr == self.sender

    def get_input(self) -> float:
        return self.input

    def get_output(self) -> float:
        return self.output

    def get_fee(self) -> float:
        return self.fee

    def valid_input_output(self) -> bool:
        return self.input > 0.0 and self.output > 0.0 and self.fee >= 0.0 and isclose(self.input, fsum((self.output, self.fee)))

    def is_valid(self) -> bool:
        if self.type == REWARD:
            # REWARD txs are valid if they are signed by the validator and have the correct value
            return (self.input == self.output == REWARD_VALUE) and self.fee == 0.0 and self.hash_is_valid() and self.signed_by(self.sender)
        else:
            # NORMAL txs are valid if they are signed by the sender and have the correct value
            return self.hash_is_valid() and self.signed_by(self.sender) and self.valid_input_output()

    def compute_hash(self) -> bytes:
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(str(self.type), 'utf8'))
        digest.update(bytes(str(self.input), 'utf8'))
        digest.update(bytes(str(self.output), 'utf8'))
        digest.update(bytes(str(self.fee), 'utf8'))
        digest.update(self.sender)
        digest.update(self.receiver)
        digest.update(bytes(str(self.created_at), 'utf8'))
        return digest.finalize()

    def __eq__(self, other: Tx) -> bool:
        return self.hash and other and self.hash == other.hash

    def __repr__(self) -> str:
        type_string = "REWARD" if self.type == REWARD else "NORMAL"
        return f"{type_string} | {self.input} from {self.sender.hex()} | {self.output} to {self.receiver.hex()} & {self.fee} fee"
