from sqlalchemy.orm import Session

from tables.blog import SessionLocal as BlogDB, Blog, Base as BlogBase, engine as blog_engine
from tables.comment import SessionLocal as CommentDB, Comment, Base as CommentBase, engine as comment_engine
from tables.gallery import SessionLocal as GalleryDB, Gallery, Base as GalleryBase, engine as gallery_engine


def seed_data():
    blog_db: Session = BlogDB()
    comment_db: Session = CommentDB()
    gallery_db: Session = GalleryDB()

    try:
      
        if blog_db.query(Blog).first():
            print("Already seeded!")
            return

       
        blog1 = Blog(
            title="اولین بلاگ",
            seo_title="first-blog",
            description="این اولین بلاگ تستی است"
        )

        blog2 = Blog(
            title="آموزش FastAPI",
            seo_title="fastapi-guide",
            description="آموزش کامل FastAPI"
        )

        blog_db.add_all([blog1, blog2])
        blog_db.commit()

        blog_db.refresh(blog1)
        blog_db.refresh(blog2)

   
        comment1 = Comment(
            post_id=blog1.id,
            name="Ali",
            email="ali@test.com",
            content="خیلی عالی بود "
        )

        comment2 = Comment(
            post_id=blog1.id,
            name="Sara",
            email="sara@test.com",
            content="ممنون از آموزش"
        )

        comment3 = Comment(
            post_id=blog2.id,
            name="Reza",
            email=None,
            content="خیلی کاربردی بود"
        )

        comment_db.add_all([comment1, comment2, comment3])
        comment_db.commit()
        
gallery1 = Gallery(
    title="نمای کاور بلاگ",
    image_url="https://example.com/img1.jpg",
    category="blog",
    alt_text="blog cover image"
)

gallery2 = Gallery(
    title="آموزش FastAPI ",
    image_url="https://example.com/img2.jpg",
    category="tutorial",
    alt_text="fastapi tutorial step 1"
)

        gallery_db.add_all([gallery1, gallery2])
        gallery_db.commit()

        print("Seed completed successfully ")

    finally:
        blog_db.close()
        comment_db.close()
        gallery_db.close()


if __name__ == "__main__":
    seed_data()