import secrets

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import jwt

secret_key = secrets.token_hex(300).encode()

with open("secret_key.txt", "wb") as f:
    f.write(secret_key)

with open("secret_key.txt", "rb") as f:
    loaded_key = f.read()

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_key_jwt = jwt.encode({"public_key": public_key_pem.decode()}, secret_key)
private_key_jwt = jwt.encode({"private_key": private_key_pem.decode()}, secret_key)

print("Public Key (JWT format):")
print(public_key_jwt)

print("\nPrivate Key (JWT format):")
print(private_key_jwt)

print(secret_key)
