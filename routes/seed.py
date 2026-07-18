from database import SessionLocal

from models.user import User
from models.blog import Blog
from models.category import Category
from models.gallery import Gallery
from models.comment import Comment

from passlib.context import CryptContext


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def get_password_hash(password: str):
    return pwd_context.hash(password)



def seed_data():

    print("DATA GENERATION STARTED")

    db = SessionLocal()

    try:

        if db.query(User).first():
            print("Already seeded!")
            return


        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin"
            },
            {
                "username": "operator",
                "email": "operator@example.com",
                "role": "operator"
            },
            {
                "username": "editor",
                "email": "editor@example.com",
                "role": "editor"
            },
            {
                "username": "user",
                "email": "user@example.com",
                "role": "user"
            }
        ]


        users = []


        for item in users_data:

            user = User(
                username=item["username"],
                email=item["email"],
                password=get_password_hash("123456"),
                role=item["role"]
            )

            db.add(user)
            users.append(user)


        db.commit()


        for user in users:
            db.refresh(user)



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

                    gallery = Gallery(
                        title=f"Gallery {g}",
                        image_url=f"https://example.com/blog_{blog.id}_{g}.jpg",
                        alt_text=f"Image {g}",
                        blog_id=blog.id
                    )

                    galleries.append(gallery)


                db.add_all(galleries)



                comments = []


                for cm in range(1, 4):

                    comment = Comment(
                        content=f"Comment {cm} for Blog {blog.id}",
                        blog_id=blog.id,
                        user_id=users[(cm - 1) % len(users)].id
                    )

                    comments.append(comment)


                db.add_all(comments)

                db.commit()



        print("DATA GENERATION COMPLETED")


    finally:

        db.close()



if __name__ == "__main__":
    seed_data()
