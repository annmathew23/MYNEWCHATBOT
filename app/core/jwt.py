import datetime as dt
import jwt
from fastapi import HTTPException, status

def create_access_token(sub: str, secret: str, alg: str, minutes: int) -> str:
    now = dt.datetime.utcnow()
    payload = {"sub": sub, "iat": now, "exp": now + dt.timedelta(minutes=minutes)}
    return jwt.encode(payload, secret, algorithm=alg)

def decode_access_token(token: str, secret: str, alg: str) -> dict:
    try:
        return jwt.decode(token, secret, algorithms=[alg])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
