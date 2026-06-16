from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models.gallery import Gallery
from schemas.gallery import GalleryCreate, GalleryUpdate
from auth.dependencies import get_current_user

router = APIRouter(prefix="/gallery", tags=["Gallery"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_gallery(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Gallery).all()


@router.post("/")
def create_gallery(data: GalleryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    item = Gallery(**data.dict(), user_id=user["user_id"])
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{id}")
def update_gallery(id: int, data: GalleryUpdate,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    item = db.query(Gallery).filter(Gallery.id == id).first()
    for k, v in data.dict(exclude_unset=True).items():
        setattr(item, k, v)

    db.commit()
    return item


@router.delete("/{id}")
def delete_gallery(id: int,
                   db: Session = Depends(get_db),
                   user=Depends(get_current_user)):

    item = db.query(Gallery).filter(Gallery.id == id).first()
    db.delete(item)
    db.commit()
    return {"message": "deleted"}