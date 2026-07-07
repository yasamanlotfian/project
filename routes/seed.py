from database import SessionLocal

from models.blog import Blog
from models.category import Category
from models.gallery import Gallery
from models.comment import Comment


def seed_data():

    print("DATA GENERATION STARTED")

    db = SessionLocal()

    try:

        if db.query(Blog).first():
            print("Already seeded!")
            return

        for c in range(1, 6):

            category = Category(
                name=f"Category {c}"
            )

            db.add(category)
            db.commit()
            db.refresh(category)

            for b in range(1, 11):

                blog = Blog(
                    title=f"Blog {c}-{b}",
                    seo_title=f"blog-{c}-{b}",
                    description=f"Description for Blog {c}-{b}",
                    content=f"Content for Blog {c}-{b}",
                    category_id=category.id
                )

                db.add(blog)
                db.commit()
                db.refresh(blog)

                galleries = []

                for g in range(1, 3):
                    galleries.append(
                        Gallery(
                            title=f"Gallery {g}",
                            image_url=f"https://example.com/blog_{blog.id}_{g}.jpg",
                            alt_text=f"Image {g}",
                            blog_id=blog.id
                        )
                    )

                db.add_all(galleries)

                comments = []

                for cm in range(1, 4):
                    comments.append(
                        Comment(
                            content=f"Comment {cm} for Blog {blog.id}",
                            blog_id=blog.id
                        )
                    )

                db.add_all(comments)

                db.commit()

        print("DATA GENERATION COMPLETED")

    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
