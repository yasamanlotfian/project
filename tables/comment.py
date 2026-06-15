from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, declarative_base, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./comment.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    post_id = Column(Integer, nullable=False)

    name = Column(String(100), nullable=False)

    email = Column(String(150), nullable=True)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/comments")
def create_comment(
    post_id: int,
    name: str,
    content: str,
    email: str = None,
    db: Session = Depends(get_db)
):

    comment = Comment(
        post_id=post_id,
        name=name,
        email=email,
        content=content
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment


@app.get("/comments")
def get_comments(db: Session = Depends(get_db)):
    return db.query(Comment).all()


@app.get("/comments/{comment_id}")
def get_comment(comment_id: int, db: Session = Depends(get_db)):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    return comment


@app.patch("/comments/{comment_id}")
def update_comment(
    comment_id: int,
    post_id: int = None,
    name: str = None,
    email: str = None,
    content: str = None,
    db: Session = Depends(get_db)
):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    if post_id is not None:
        comment.post_id = post_id

    if name is not None:
        comment.name = name

    if email is not None:
        comment.email = email

    if content is not None:
        comment.content = content

    db.commit()
    db.refresh(comment)

    return comment


@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db)):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted"}

