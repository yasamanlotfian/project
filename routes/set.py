from fastapi import FastAPI
from routes import blog, gallery, comment

app = FastAPI()

app.include_router(blog.router)
app.include_router(gallery.router)
app.include_router(comment.router)