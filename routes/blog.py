from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc

from database import get_db
from models.blog import Blog
from schemas import BlogCreate, BlogResponse


router = APIRouter(
    prefix="/blog",
    tags=["Blog"]
)


# CREATE
@router.post("/", response_model=BlogResponse)
def create_blog(
    blog: BlogCreate,
    db: Session = Depends(get_db)
):

    new_blog = Blog(
        title=blog.title,
        seo_title=blog.seo_title,
        description=blog.description,
        content=blog.content,
        category_id=blog.category_id
    )

    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return (
        db.query(Blog)
        .options(
            joinedload(Blog.category),
            joinedload(Blog.galleries),
            joinedload(Blog.comments)
        )
        .filter(Blog.id == new_blog.id)
        .first()
    )


# GET ALL
@router.get("/")
def get_blogs(
    page: int = 1,
    size: int = 5,
    search: str | None = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):

    query = (
        db.query(Blog)
        .options(
            joinedload(Blog.category),
            joinedload(Blog.galleries),
            joinedload(Blog.comments)
        )
    )

    # Search
    if search:
        query = query.filter(
            Blog.title.ilike(f"%{search}%")
        )

    # Sort
    sort_columns = {
        "id": Blog.id,
        "title": Blog.title,
        "view_num": Blog.view_num,
        "created_at": Blog.created_at,
        "updated_at": Blog.updated_at,
    }

    column = sort_columns.get(sort_by, Blog.id)

    if sort_order.lower() == "desc":
        query = query.order_by(desc(column))
    else:
        query = query.order_by(asc(column))

    total = query.count()

    blogs = (
        query
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": blogs
    }


# GET ONE
@router.get("/{blog_id}", response_model=BlogResponse)
def get_blog(
    blog_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):

    blog = (
        db.query(Blog)
        .options(
            joinedload(Blog.category),
            joinedload(Blog.galleries),
            joinedload(Blog.comments)
        )
        .filter(Blog.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    cookie_name = f"blog_view_{blog_id}"

    if request.cookies.get(cookie_name) is None:

        blog.view_num += 1
        db.commit()

        response.set_cookie(
            key=cookie_name,
            value="viewed",
            max_age=1800,
            httponly=True
        )

        db.refresh(blog)

    return blog


# UPDATE
@router.patch("/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: int,
    blog_data: BlogCreate,
    db: Session = Depends(get_db)
):

    blog = db.query(Blog).filter(Blog.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    blog.title = blog_data.title
    blog.seo_title = blog_data.seo_title
    blog.description = blog_data.description
    blog.content = blog_data.content
    blog.category_id = blog_data.category_id

    db.commit()
    db.refresh(blog)

    return (
        db.query(Blog)
        .options(
            joinedload(Blog.category),
            joinedload(Blog.galleries),
            joinedload(Blog.comments)
        )
        .filter(Blog.id == blog_id)
        .first()
    )


# DELETE
@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):

    blog = db.query(Blog).filter(Blog.id == blog_id).first()

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
