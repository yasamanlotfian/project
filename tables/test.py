from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Blog(Base):
    __tablename__ = "blog"  

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    seo_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    comment_id = Column(Integer, nullable=True)
    gallery_id = Column(Integer, nullable=True)

    view_num = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/blogs")
def create_blog(title: str, seo_title: str, description: str, db: Session = Depends(get_db)):
    blog = Blog(
        title=title,
        seo_title=seo_title,
        description=description
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@app.get("/blogs")
def get_blogs(db: Session = Depends(get_db)):
    return db.query(Blog).all()



@app.get("/blogs/{blog_id}")
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    return blog



@app.patch("/blogs/{blog_id}")
def update_blog(
    blog_id: int,
    title: str = None,
    seo_title: str = None,
    description: str = None,
    db: Session = Depends(get_db)
):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    if title is not None:
        blog.title = title
    if seo_title is not None:
        blog.seo_title = seo_title
    if description is not None:
        blog.description = description

    db.commit()
    db.refresh(blog)
    return blog


@app.delete("/blogs/{blog_id}")
def delete_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()

    return {"message": "Blog deleted successfully"}