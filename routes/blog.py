from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.blog import Blog
from models.user import User
from auth.dependencies import (
    get_current_user,
    require_level
)

router = APIRouter(
    prefix="/blog",
    tags=["Blog"]
)


@router.get("/")
def get_blogs(
    page: int = 1,
    size: int = 5,
    search: str = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Blog)

    if search:
        query = query.filter(
            Blog.title.ilike(f"%{search}%")
        )

    allowed_sort_fields = [
        "id",
        "title",
        "seo_title",
        "created_at"
    ]

    if sort_by in allowed_sort_fields:
        column = getattr(Blog, sort_by)

        if sort_order == "asc":
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())
    else:
        query = query.order_by(Blog.id.desc())

    total = query.count()

    items = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": items
    }

@router.post("/")
def create_blog(
    title: str,
    seo_title: str,
    description: str,
    category_id: int,
    content: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_level(3))
):

    blog = Blog(
        title=title,
        seo_title=seo_title,
        description=description,
        content=content,
        category_id=category_id
    )

    db.add(blog)
    db.commit()
    db.refresh(blog)

    return blog



@router.patch("/{blog_id}")
def update_blog(
    blog_id: int,
    title: str = None,
    seo_title: str = None,
    description: str = None,
    content: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_level(3))
):

    blog = db.query(Blog).filter(
        Blog.id == blog_id
    ).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    if title is not None:
        blog.title = title

    if seo_title is not None:
        blog.seo_title = seo_title

    if description is not None:
        blog.description = description

    if content is not None:
        blog.content = content

    db.commit()
    db.refresh(blog)

    return blog



@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_level(3))
):

    blog = (
        db.query(Blog)
        .filter(Blog.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    db.delete(blog)
    db.commit()

    return {
        "message": "Blog deleted successfully"
    }
