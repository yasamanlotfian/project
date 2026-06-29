from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models.blog import Blog
from schemas.blog import BlogCreate, BlogUpdate

router = APIRouter(prefix="/blog", tags=["Blog"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_blogs(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    skip = (page - 1) * size

    blogs = db.query(Blog).offset(skip).limit(size).all()
    total = db.query(Blog).count()

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": blogs
    }

@router.get("/{blog_id}")
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return {"error": "not found"}

    blog.view_num += 1
    db.commit()
    db.refresh(blog)

    return blog


@router.post("/")
def create_blog(data: BlogCreate, db: Session = Depends(get_db)):
    blog = Blog(**data.dict(), view_num=0)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.patch("/{blog_id}")
def update_blog(blog_id: int, data: BlogUpdate, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return {"error": "not found"}

    for key, value in data.dict(exclude_unset=True).items():
        setattr(blog, key, value)

    db.commit()
    db.refresh(blog)
    return blog

@router.delete("/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        return {"error": "not found"}

    db.delete(blog)
    db.commit()
    return {"message": "deleted"}
