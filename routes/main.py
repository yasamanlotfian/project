from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import blog, gallery, comment

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog.router)
app.include_router(gallery.router)
app.include_router(comment.router)