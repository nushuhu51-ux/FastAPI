from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    rating: Optional[int] = None


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    return {"data": "This is your posts"}


@app.post("/createposts")
def create_posts(new_post: Post):
    print(new_post.rating)
    return {"data": new_post}