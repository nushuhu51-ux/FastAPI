from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()




class Post(BaseModel):
    title: str
    content: str
    publish: bool = True


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastAPI', user='postgres',
                                password='sami2539E', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)


my_posts = [
    {
        "title": "title of post 1",
        "content": "content of post 1",
        "id": 1
    },
    {
        "title": "favorite foods",
        "content": "I like pizza",
        "id": 2
    }
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i




@app.get("/")
def root():
    return {"message": "Hello World"}



@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}




@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    new_post = cursor.execute("""INSERT INTO posts (title, content, published) VALUES(%s, %s, %s) 
    RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    
    return {"data": new_post}




@app.get("/posts/{id}")
def get_post(id: str):
    cursor.execute("""SELECT * from posts WHERE id = %s""", (str(id)))
    test_post = cursor.fetchone()
    post = find_post(id)
    print(test_post)
    post = find_post(id)

    if not post:
        
        raise HTTPException(
            status_code=404,
            detail=f"Post with id {id} does not exist"
        )
    return {"post_detail": post}



@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()




    if deleted_post ==  None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id: {id} does not exist."
        )
   
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: str, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content =%s, published=%s RETURNING """,
                    (post.title, post.content, post.published, str(id)))

    updated_post = cursor.fetchone()
    conn.commit()

  

    if updated_post == None:
        raise HTTPException(
            status_code=404,
            detail=f"Post with id: {id} does not exist."
        )
    

   
    return {"data": updated_post}