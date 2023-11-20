#!/usr/bin/env python3
"""
"""

from cryptography.exceptions import *
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


def generate_keys() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

# Sign a passed message using a given private key
# Make sure the message is encoded correctly before signing
# Signing and verifying algorithms must be the same


def sign(message: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
    signed = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256())
    return signed


# Verify a signature for a message using a given public key
# Make sure the message is decoded correctly before verifying
# Signing and verifying algorithms values must be the same
def verify(message: bytes, signature: bytes, public_key: rsa.RSAPublicKey) -> bool:
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        return True
    except InvalidSignature:
        return False


def encode_keys(keys: tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey], pw: str) -> tuple[bytes, bytes]:
    prv_key, pbc_key = keys
    priv = prv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            pw.encode('utf8'))
    )
    pub = pbc_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv, pub


def decode_keys(keys: tuple[bytes, bytes], pw: str) -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    prv_key, pbc_key = keys

    priv = serialization.load_pem_private_key(
        prv_key,
        password=pw.encode('utf8'),
    )
    pub = serialization.load_pem_public_key(
        pbc_key
    )
    return priv, pub


def decode_public_key(key: bytes) -> rsa.RSAPublicKey:
    return serialization.load_pem_public_key(key)


def encode_public_key(key: rsa.RSAPublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
