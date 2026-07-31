from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Connect to PostgreSQL
while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastAPI",
            user="postgres",
            password="sami2539E",
            cursor_factory=RealDictCursor
        )

        cursor = conn.cursor()
        print("Database connection was successful!")
        break

    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


@app.get("/")
def root():
    return {"message": "Hello World"}


# Get all posts
@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data": posts}


# Create a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(
        """
        INSERT INTO posts (title, content, published)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (post.title, post.content, post.published)
    )

    new_post = cursor.fetchone()
    conn.commit()

    return {"data": new_post}


# Get one post
@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(
        """
        SELECT * FROM posts
        WHERE id = %s
        """,
        (id,)
    )

    post = cursor.fetchone()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )

    return {"data": post}


# Delete a post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        """
        DELETE FROM posts
        WHERE id = %s
        RETURNING *
        """,
        (id,)
    )

    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Update a post
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """
        UPDATE posts
        SET title = %s,
            content = %s,
            published = %s
        WHERE id = %s
        RETURNING *
        """,
        (
            post.title,
            post.content,
            post.published,
            id
        )
    )

    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist"
        )

    return {"data": updated_post}