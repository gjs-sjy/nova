import hashlib
import secrets


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(email):
    return secrets.token_hex(16)


def verify_token(token):
    # Was going to be used for auth middleware.
    return len(token) == 32
