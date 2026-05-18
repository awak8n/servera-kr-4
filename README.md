# КР №4

## Структура проекта

```
├── app.py                          # Главное приложение
├── models.py                       # SQLAlchemy + Pydantic модели
├── database.py                     # Подключение к БД
├── exceptions.py                   # Кастомные исключения и обработчики
├── alembic.ini                     # Конфигурация Alembic
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_create_products.py  # Миграция 1: создание таблицы
│       └── 0002_add_description.py  # Миграция 2: добавление description
├── tests/
│   ├── conftest.py                  # Фикстуры pytest
│   ├── test_users.py                # Async тесты /users (задание 11.2)
│   ├── test_exceptions.py           # Тесты кастомных исключений (10.1)
│   └── test_validation.py           # Тесты валидации (10.2)
├── requirements.txt
└── pytest.ini
```

---

## Установка и запуск

```bash
pip install -r requirements.txt

# Применить миграции Alembic (создаст app.db с таблицей products)
alembic upgrade head

# Запустить приложение
uvicorn app:app --reload
```

---

## Задание 9.1 — Alembic миграции

```bash
# Применить все миграции (создаёт таблицу + добавляет description)
alembic upgrade head

# Посмотреть историю миграций
alembic history

# Откатить одну миграцию
alembic downgrade -1

# Откатить всё
alembic downgrade base
```

**Последовательность миграций:**
1. `0001_create_products` — создаёт таблицу `products` (id, title, price, count) и добавляет 2 записи
2. `0002_add_description` — добавляет колонку `description NOT NULL` и обновляет существующие записи

---

## Задание 10.1 — Кастомные исключения

| Исключение | Статус | error_code |
|---|---|---|
| `CustomExceptionA` | 422 | `BUSINESS_RULE_VIOLATED` |
| `CustomExceptionB` | 404 | `RESOURCE_NOT_FOUND` |
| `InsufficientStockException` | 409 | `INSUFFICIENT_STOCK` |

```bash
# Вызвать CustomExceptionA (цена <= 0)
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"title":"Bad","price":-1,"count":1,"description":"test"}'

# Вызвать CustomExceptionB (не найден)
curl http://localhost:8000/products/99999

# Вызвать InsufficientStockException
curl -X POST "http://localhost:8000/products/1/buy?quantity=9999"
```

---

## Задание 10.2 — Валидация пользователя

```bash
# Корректные данные
curl -X POST http://localhost:8000/users/validate \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","age":25,"email":"alice@example.com","password":"securepass"}'

# Ошибка: возраст <= 18, невалидный email
curl -X POST http://localhost:8000/users/validate \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","age":15,"email":"not-email","password":"pass"}'
```

---

## Задания 11.1 / 11.2 — Запуск тестов

```bash
# Все тесты
pytest

# Только async тесты пользователей
pytest tests/test_users.py -v

# Тесты исключений
pytest tests/test_exceptions.py -v

# Тесты валидации
pytest tests/test_validation.py -v

# С покрытием (если установлен pytest-cov)
pytest --cov=app tests/
```

Все тесты должны завершиться со статусом **passed**.

---

## API маршруты

| Метод | Путь | Описание |
|---|---|---|
| POST | `/products` | Создать продукт |
| GET | `/products` | Список продуктов |
| GET | `/products/{id}` | Получить продукт |
| PUT | `/products/{id}` | Обновить продукт |
| DELETE | `/products/{id}` | Удалить продукт |
| POST | `/products/{id}/buy` | Купить (проверка остатка) |
| POST | `/users/validate` | Валидация пользователя |
| POST | `/users` | Создать in-memory пользователя |
| GET | `/users/{id}` | Получить пользователя |
| DELETE | `/users/{id}` | Удалить пользователя |
