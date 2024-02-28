import secrets

def unique_security_token():
    return str(secrets.token_hex())