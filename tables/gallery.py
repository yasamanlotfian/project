from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./gallery.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()



class Gallery(Base):
    __tablename__ = "galleries"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    image_url = Column(String(500), nullable=False)

    category = Column(String(100), nullable=True)

    alt_text = Column(String(255), nullable=True)

created_at = Column(DateTime, server_default=func.now())


app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@app.post("/gallery")
def create_gallery(
    title: str,
    image_url: str,
    category: str = None,
    alt_text: str = None,
    db: Session = Depends(get_db)
):

    gallery = Gallery(
        title=title,
        image_url=image_url,
        category=category,
        alt_text=alt_text
    )

    db.add(gallery)
    db.commit()
    db.refresh(gallery)

    return gallery

@app.get("/gallery")
def get_galleries(db: Session = Depends(get_db)):
    return db.query(Gallery).all()



@app.get("/gallery/{gallery_id}")
def get_gallery(gallery_id: int, db: Session = Depends(get_db)):

    gallery = db.query(Gallery).filter(Gallery.id == gallery_id).first()

    if gallery is None:
        raise HTTPException(status_code=404, detail="Gallery not found")

    return gallery


@app.patch("/gallery/{gallery_id}")
def update_gallery(
    gallery_id: int,
    title: str = None,
    image_url: str = None,
    category: str = None,
    alt_text: str = None,
    db: Session = Depends(get_db)
):

    gallery = db.query(Gallery).filter(Gallery.id == gallery_id).first()

    if gallery is None:
        raise HTTPException(status_code=404, detail="Gallery not found")

    if title is not None:
        gallery.title = title

    if image_url is not None:
        gallery.image_url = image_url

    if category is not None:
        gallery.category = category

    if alt_text is not None:
        gallery.alt_text = alt_text

    db.commit()
    db.refresh(gallery)

    return gallery



@app.delete("/gallery/{gallery_id}")
def delete_gallery(gallery_id: int, db: Session = Depends(get_db)):

    gallery = db.query(Gallery).filter(Gallery.id == gallery_id).first()

    if gallery is None:
        raise HTTPException(status_code=404, detail="Gallery not found")

    db.delete(gallery)
    db.commit()

    return {"message": "Gallery deleted"}