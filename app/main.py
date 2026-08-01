from fastapi import FastAPI, Response, status, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models, schemas, utils


# Create database tables
models.Base.metadata.create_all(bind=engine)


# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


# Get all posts
@app.get("/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()

    return posts


# Create a post
@app.post(
    "/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post
)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db)
):

    new_post = models.Post(
        **post.model_dump()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# Get one post
@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(
    id: int,
    db: Session = Depends(get_db)
):

    post = (
        db.query(models.Post)
        .filter(models.Post.id == id)
        .first()
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )

    return post


# Delete a post
@app.delete(
    "/posts/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_post(
    id: int,
    db: Session = Depends(get_db)
):

    post_query = (
        db.query(models.Post)
        .filter(models.Post.id == id)
    )

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist"
        )

    post_query.delete(
        synchronize_session=False
    )

    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# Update a post
@app.put(
    "/posts/{id}",
    response_model=schemas.Post
)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db)
):

    post_query = (
        db.query(models.Post)
        .filter(models.Post.id == id)
    )

    existing_post = post_query.first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist"
        )

    post_query.update(
        post.model_dump(),
        synchronize_session=False
    )

    db.commit()

    return post_query.first()


# Create user
@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserOut
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):

    # Check existing email
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )


    # Hash password
    hashed_password = utils.hash_password(
        user.password
    )


    new_user = models.User(**user.dict())


    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_user(
    id: int,
    db: Session = Depends(get_db)
):

    user = (
        db.query(models.User)
        .filter(models.User.id == id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} was not found"
        )

    return user