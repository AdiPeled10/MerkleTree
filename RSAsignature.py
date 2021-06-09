from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import base64



class RSAsignature:
    _PUBLIC_KEY = 65537

    @staticmethod
    def generate(key_size=2048):
        private_key = rsa.generate_private_key(public_exponent=RSAsignature._PUBLIC_KEY,
                                               key_size=key_size, backend=default_backend())
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    @staticmethod
    def sign(data: bytes, pem_private_key):
        private_key = serialization.load_pem_private_key(pem_private_key, None, default_backend())

        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature)

    @staticmethod
    def verify(data, pem_public_key, signature):
        public_key = serialization.load_pem_public_key(pem_public_key, default_backend())

        flag = public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return flag

