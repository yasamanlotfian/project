from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta



SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



SECRET_KEY = "secret"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_token(data: dict):
    payload = data.copy()
    payload.update({"exp": datetime.utcnow() + timedelta(hours=2)})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer)

class Gallery(Base):
    __tablename__ = "galleries"
    id = Column(Integer, primary_key=True)
    image_url = Column(String)
    user_id = Column(Integer)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    blog_id = Column(Integer)
    user_id = Column(Integer)

Base.metadata.create_all(bind=engine)

app = FastAPI()


class UserCreate(BaseModel):
    username: str
    password: str

class BlogCreate(BaseModel):
    title: str
    content: str

class GalleryCreate(BaseModel):
    image_url: str

class CommentCreate(BaseModel):
    text: str
    blog_id: int



def get_object_or_404(model, db: Session, obj_id: int):
    obj = db.query(model).filter(model.id == obj_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj



@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed = pwd_context.hash(user.password)
    new_user = User(username=user.username, password=hashed)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "registered"}


@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/blogs")
def create_blog(data: BlogCreate,
                db: Session = Depends(get_db),
                user=Depends(get_current_user)):

    blog = Blog(
        title=data.title,
        content=data.content,
        user_id=user
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@app.get("/blogs")
def get_blogs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Blog).all()

@app.delete("/blogs/{id}")
def delete_blog(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = get_object_or_404(Blog, db, id)
    db.delete(obj)
    db.commit()
    return {"message": "deleted"}


@app.post("/galleries")
def create_gallery(data: GalleryCreate,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    obj = Gallery(image_url=data.image_url, user_id=user)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/galleries")
def get_galleries(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Gallery).all()


@app.post("/comments")
def create_comment(data: CommentCreate,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    obj = Comment(
        text=data.text,
        blog_id=data.blog_id,
        user_id=user
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/comments")
def get_comments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Comment).all()