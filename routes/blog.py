from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.blog import Blog
from schemas.blog import BlogCreate, BlogUpdate
from auth.dependencies import get_current_user

router = APIRouter(prefix="/blog", tags=["Blog"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_blogs(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Blog).all()


@router.post("/")
def create_blog(data: BlogCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    blog = Blog(**data.dict(), user_id=user["user_id"])
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.patch("/{blog_id}")
def update_blog(blog_id: int, data: BlogUpdate,
                db: Session = Depends(get_db),
                user=Depends(get_current_user)):

    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    for key, value in data.dict(exclude_unset=True).items():
        setattr(blog, key, value)

    db.commit()
    return blog


@router.delete("/{blog_id}")
def delete_blog(blog_id: int,
                db: Session = Depends(get_db),
                user=Depends(get_current_user)):

    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    db.delete(blog)
    db.commit()
    return {"message": "deleted"}