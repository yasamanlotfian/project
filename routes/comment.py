from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.comment import Comment
from models.user import User
from schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse
)
from auth.dependencies import get_current_user


router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)


@router.post(
    "/",
    response_model=CommentResponse
)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_comment = Comment(
        content=comment.content,
        blog_id=comment.blog_id,
        user_id=current_user.id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.get(
    "/me",
    response_model=list[CommentResponse]
)
def my_comments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return (
        db.query(Comment)
        .filter(Comment.user_id == current_user.id)
        .all()
    )

@router.patch(
    "/{comment_id}",
    response_model=CommentResponse
)
def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db_comment = (
        db.query(Comment)
        .filter(
            Comment.id == comment_id,
            Comment.user_id == current_user.id
        )
        .first()
    )

    if not db_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if comment.content is not None:
        db_comment.content = comment.content

    db.commit()
    db.refresh(db_comment)

    return db_comment


@router.delete(
    "/{comment_id}"
)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    db_comment = (
        db.query(Comment)
        .filter(
            Comment.id == comment_id,
            Comment.user_id == current_user.id
        )
        .first()
    )

    if not db_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    db.delete(db_comment)
    db.commit()

    return {
        "message": "Comment deleted successfully"
    }