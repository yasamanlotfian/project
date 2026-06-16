from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.comment import Comment
from schemas.comment import CommentCreate, CommentUpdate
from auth.dependencies import get_current_user

router = APIRouter(prefix="/comment", tags=["Comment"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_comments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Comment).all()


@router.post("/")
def create_comment(data: CommentCreate,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    comment = Comment(**data.dict(), user_id=user["user_id"])
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.patch("/{id}")
def update_comment(id: int, data: CommentUpdate,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    comment = db.query(Comment).filter(Comment.id == id).first()

    for k, v in data.dict(exclude_unset=True).items():
        setattr(comment, k, v)

    db.commit()
    return comment


@router.delete("/{id}")
def delete_comment(id: int,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    comment = db.query(Comment).filter(Comment.id == id).first()
    db.delete(comment)
    db.commit()
    return {"message": "deleted"}