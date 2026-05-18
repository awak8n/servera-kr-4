from itertools import count
from threading import Lock
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Base, Product, ProductCreate, ProductOut, UserSchema, UserIn, UserOut
from exceptions import (
    CustomExceptionA, CustomExceptionB, InsufficientStockException,
    custom_exception_a_handler, custom_exception_b_handler, insufficient_stock_handler,
    ErrorResponse,
)

# Создаём таблицы (если не используем миграции Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI КР4")

# Регистрация обработчиков исключений
app.add_exception_handler(CustomExceptionA, custom_exception_a_handler)
app.add_exception_handler(CustomExceptionB, custom_exception_b_handler)
app.add_exception_handler(InsufficientStockException, insufficient_stock_handler)


# Задание 10.2

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"])
        errors.append({"field": field, "message": err["msg"], "type": err["type"]})
    print(f"[VALIDATION ERROR] path={request.url.path} | errors={errors}")
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Request data validation failed.",
            "errors": errors,
        },
    )


# Задание 9.1

@app.post("/products", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    if data.price <= 0:
        raise CustomExceptionA(detail=f"Price must be positive, got {data.price}")
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise CustomExceptionB(detail=f"Product with id={product_id} not found")
    return product


@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductCreate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise CustomExceptionB(detail=f"Product with id={product_id} not found")
    if data.price <= 0:
        raise CustomExceptionA(detail=f"Price must be positive, got {data.price}")
    for field, value in data.model_dump().items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise CustomExceptionB(detail=f"Product with id={product_id} not found")
    db.delete(product)
    db.commit()


# Демо-маршрут
@app.post("/products/{product_id}/buy")
def buy_product(product_id: int, quantity: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise CustomExceptionB(detail=f"Product with id={product_id} not found")
    if product.count < quantity:
        raise InsufficientStockException(
            detail=f"Requested {quantity}, available {product.count}"
        )
    product.count -= quantity
    db.commit()
    return {"message": f"Purchased {quantity} × '{product.title}'"}


# Задание 10.2

@app.post("/users/validate", status_code=201)
def validate_user(user: UserSchema):
    return {
        "message": f"User '{user.username}' is valid",
        "data": user.model_dump(),
    }


# Задание 11.1 / 11.2

_id_seq = count(start=1)
_id_lock = Lock()
db_users: dict[int, dict] = {}


def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    user_id = next_user_id()
    db_users[user_id] = user.model_dump()
    return {"id": user_id, **db_users[user_id]}


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in db_users:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db_users[user_id]}


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if db_users.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
