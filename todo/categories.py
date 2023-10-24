from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from . import models
from . import auth
from .database import db_dependency


router = APIRouter(prefix="/categories", tags=["categories"])


user_dependency = Annotated[dict, Depends(auth.get_current_user)]


class CreateCategoryRequest(BaseModel):
    name: str


class PatchCategoryRequest(BaseModel):
    name: str = None


class Category(BaseModel):
    id: int
    name: str

    @classmethod
    def from_db(cls, category: models.Category):
        return cls(id=category.id, name=category.name)


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_category(
    user: user_dependency,
    db: db_dependency,
    create_category_request: CreateCategoryRequest,
) -> Category:
    category = models.Category(user_id=user["id"], name=create_category_request.name)
    db.add(category)
    db.commit()

    return Category.from_db(category)


@router.get("/")
def get_categories(user: user_dependency, db: db_dependency) -> list[Category]:
    categories = db.query(models.Category).filter_by(user_id=user["id"]).all()
    return [Category.from_db(category) for category in categories]


@router.get("/{category_id}")
def get_category(
    user: user_dependency, db: db_dependency, category_id: int
) -> Category:
    category = (
        db.query(models.Category).filter_by(user_id=user["id"], id=category_id).first()
    )

    if not category:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category is not found")

    return Category.from_db(category)


@router.patch("/{category_id}")
def edit_category(
    user: user_dependency,
    db: db_dependency,
    category_id: int,
    patch_category_request: PatchCategoryRequest,
):
    category = (
        db.query(models.Category).filter_by(user_id=user["id"], id=category_id).first()
    )

    if not category:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category is not found")

    category.name = patch_category_request.name

    db.commit()


@router.delete("/{category_id}")
def delete_category(
    user: user_dependency,
    db: db_dependency,
    category_id: int,
):
    category = (
        db.query(models.Category).filter_by(user_id=user["id"], id=category_id).first()
    )

    if not category:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Category is not found")

    category_tasks = db.query(models.Task).filter_by(category_id=category_id).all()
    for task in category_tasks:
        task.category = None

    db.delete(category)
    db.commit()
