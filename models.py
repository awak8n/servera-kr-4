from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel, EmailStr, conint, constr
from typing import Optional


class Base(DeclarativeBase):
    pass


# Задание 9.1
class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    title       = Column(String(255), nullable=False)
    price       = Column(Float, nullable=False)
    count       = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=False, server_default="")


# Pydantic схемы
class ProductCreate(BaseModel):
    title: str
    price: float
    count: int
    description: str = ""


class ProductOut(BaseModel):
    id: int
    title: str
    price: float
    count: int
    description: str

    model_config = {"from_attributes": True}


# Задание 10.2
class UserSchema(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


# Задание 11.1 / 11.2
class UserIn(BaseModel):
    username: str
    age: int


class UserOut(BaseModel):
    id: int
    username: str
    age: int
