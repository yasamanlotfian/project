from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import jwt
from jwt import PyJWTError

app = FastAPI()

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


hashed_default_password = pwd_context.hash("1234")

users_db = {
    "yasaman": {
        "username": "yasaman",
        "hashed_password": hashed_default_password,
    }
}

class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str

class UserUpdate(BaseModel):
    password: str | None = None


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_user(username: str):
    data = users_db.get(username)
    return UserInDB(**data) if data else None


def authenticate_user(username: str, password: str):
    user = get_user(username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_access_token(data: dict, expires_minutes: int = 15):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload.update({"exp": expire})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if not username:
            raise credentials_error

    except PyJWTError:
        raise credentials_error

    user = get_user(username)

    if not user:
        raise credentials_error

    return user


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": user.username},
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/users/me", response_model=User)
def read_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user


@app.patch("/users/me", response_model=User)
def update_me(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
):
    if user_update.password:
        users_db[current_user.username]["hashed_password"] = pwd_context.hash(
            user_update.password
        )

    return User(username=current_user.username)


@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(current_user: UserInDB = Depends(get_current_user)):
    users_db.pop(current_user.username, None)
