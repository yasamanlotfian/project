from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt



SECRET_KEY = "secret"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



def create_token(data: dict):
   
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None



def get_current_user(token: str = Depends(oauth2_scheme)):

    user = verify_token(token)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return user