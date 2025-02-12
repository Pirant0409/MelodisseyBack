from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.config import SECRET_KEY, ALGORITHM
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/protected")

def verify_admin_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != "admin":
            raise HTTPException(status_code=403, detail="Not authorized")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")