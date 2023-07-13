import os

import jwt
from datetime import datetime, timedelta

from fastapi import HTTPException

file_path_secret_key = os.path.join('app', "helper", 'secret_key.txt')


class JWTManager:
    def __init__(self,
                 secret_key='d4910867eea1c9990e91e04ae769b74b25d93801e0844aac2e3a8b1a458538473b901ecbe3651d458ebfb38925bdda78ea713ed46a8cc398cccdb2a01fd3c4dec7f78e067759bdd6afa18343657916adca157957e010ffe27f0a399ec3a52e86d81095fd866c23a5ab0456367db517e8ec250b09893de516facb054541cea70807044446cdd68a96da1e0c0f31500998c1628ee7cdbd'):
        with open(file_path_secret_key, "rb") as f:
            loaded_key = f.read()

        self.secret_key = loaded_key

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None, algorithm="HS256"):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=500)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=algorithm)
        return encoded_jwt

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])

            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
