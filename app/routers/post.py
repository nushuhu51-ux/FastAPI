from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from.. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db
import app


router = APIRouter()
# ---------------------- POSTS ----------------------

@router.get("/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()


@router.post(
    "/posts",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.Post
)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db)
):
    new_post = models.Post(**post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/posts/{id}", response_model=schemas.Post)
def get_post(
    id: int,
    db: Session = Depends(get_db)
):
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found"
        )

    return post


@router.delete(
    "/posts/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_post(
    id: int,
    db: Session = Depends(get_db)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist"
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/posts/{id}",
    response_model=schemas.Post
)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    existing_post = post_query.first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} does not exist"
        )

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()


# ---------------------- USERS ----------------------

@router.post("/users",status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(
    user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hashed password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
  

    # Create SQLAlchemy model
    new_user = models.User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/users/{id}", response_model=schemas.UserOut)
def get_user(
    id: int, db: Session = Depends(get_db)):
    user = (db.query(models.User).filter(models.User.id == id).first())

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} was not found"
        )

    return user