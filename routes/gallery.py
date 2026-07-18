from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from sqlalchemy.orm import Session

from database import get_db
from services.image_crop import crop_image

from models.gallery import Gallery
from models.blog import Blog
from models.user import User

from auth.dependencies import admin_or_operator

import os
import shutil
import uuid

from PIL import Image


router = APIRouter(
    prefix="/gallery",
    tags=["Gallery"]
)

UPLOAD_ORIGINAL_DIR = "uploads/gallery/original"
UPLOAD_WEBP_DIR = "uploads/gallery/webp"


@router.get("/")
def get_gallery(
    page: int = 1,
    size: int = 5,
    search: str = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):

    query = db.query(Gallery)

    if search:
        query = query.filter(
            Gallery.title.ilike(f"%{search}%")
        )

    allowed_sort_fields = [
        "id",
        "title",
        "created_at",
        "original_file_size",
        "optimized_file_size"
    ]

    if sort_by in allowed_sort_fields:

        column = getattr(Gallery, sort_by)

        if sort_order == "asc":
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())

    else:
        query = query.order_by(Gallery.id.desc())

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


@router.get("/{gallery_id}")
def get_gallery_by_id(
    gallery_id: int,
    db: Session = Depends(get_db)
):

    gallery = (
        db.query(Gallery)
        .filter(Gallery.id == gallery_id)
        .first()
    )

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found"
        )

    return gallery


@router.post("/upload")
def upload_image(
    blog_id: int,
    title: str,
    alt_text: str = "",
    file: UploadFile = File(...),
    current_user: User = Depends(admin_or_operator),
    db: Session = Depends(get_db)
):

    blog = db.query(Blog).filter(
        Blog.id == blog_id
    ).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    os.makedirs(
        UPLOAD_ORIGINAL_DIR,
        exist_ok=True
    )

    os.makedirs(
        UPLOAD_WEBP_DIR,
        exist_ok=True
    )

    extension = os.path.splitext(
        file.filename
    )[1]

    filename = f"{uuid.uuid4()}{extension}"

    original_path = os.path.join(
        UPLOAD_ORIGINAL_DIR,
        filename
    )

    with open(original_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )
    webp_filename = f"{uuid.uuid4()}.webp"

    webp_path = os.path.join(
        UPLOAD_WEBP_DIR,
        webp_filename
    )
    image = Image.open(original_path)


    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    image = crop_image(image) 

    image.save(
       webp_path,
       "WEBP",
       optimize=True,
       quality=80
)    

    original_size = os.path.getsize(
        original_path
    )

    optimized_size = os.path.getsize(
        webp_path
    )

    gallery = Gallery(
        title=title,
        alt_text=alt_text,
        original_image_url=original_path.replace("\\", "/"),
        optimized_image_url=webp_path.replace("\\", "/"),
        original_file_size=original_size,
        optimized_file_size=optimized_size,
        mime_type="image/webp",
        blog_id=blog_id
    )

    db.add(gallery)
    db.commit()
    db.refresh(gallery)

    return gallery


@router.patch("/{gallery_id}")
def update_gallery(
    gallery_id: int,
    title: str = None,
    alt_text: str = None,
    file: UploadFile = File(None),
    current_user: User = Depends(admin_or_operator),
    db: Session = Depends(get_db)
):

    gallery = (
        db.query(Gallery)
        .filter(Gallery.id == gallery_id)
        .first()
    )

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found"
        )

    if title is not None:
        gallery.title = title

    if alt_text is not None:
        gallery.alt_text = alt_text

    if file is not None:

        if os.path.exists(gallery.original_image_url):
            os.remove(gallery.original_image_url)

        if os.path.exists(gallery.optimized_image_url):
            os.remove(gallery.optimized_image_url)

        extension = os.path.splitext(file.filename)[1]

        filename = f"{uuid.uuid4()}{extension}"

        original_path = os.path.join(
            UPLOAD_ORIGINAL_DIR,
            filename
        )

        with open(original_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )
        webp_filename = f"{uuid.uuid4()}.webp"

        webp_path = os.path.join(
            UPLOAD_WEBP_DIR,
            webp_filename
        )

        image = Image.open(original_path)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image = crop_image(image)

        image.save(
            webp_path,
            "WEBP",
            optimize=True,
            quality=80
        )

        gallery.original_image_url = original_path.replace("\\", "/")
        gallery.optimized_image_url = webp_path.replace("\\", "/")
        gallery.original_file_size = os.path.getsize(original_path)
        gallery.optimized_file_size = os.path.getsize(webp_path)
        gallery.mime_type = "image/webp"

    db.commit()
    db.refresh(gallery)

    return gallery

@router.delete("/{gallery_id}")
def delete_gallery(
    gallery_id: int,
    current_user: User = Depends(admin_or_operator),
    db: Session = Depends(get_db)
):

    gallery = (
        db.query(Gallery)
        .filter(Gallery.id == gallery_id)
        .first()
    )

    if not gallery:
        raise HTTPException(
            status_code=404,
            detail="Gallery not found"
        )

    if (
        gallery.original_image_url
        and
        os.path.exists(gallery.original_image_url)
    ):
        os.remove(
            gallery.original_image_url
        )

    if (
        gallery.optimized_image_url
        and
        os.path.exists(gallery.optimized_image_url)
    ):
        os.remove(
            gallery.optimized_image_url
        )

    db.delete(gallery)
    db.commit()

    return {
        "message": "Gallery deleted successfully"
    }


