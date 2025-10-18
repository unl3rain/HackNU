# SmartBot Backend (FastAPI)

Локальный запуск (без Docker):

1. Создайте виртуальное окружение и установите зависимости:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Создайте `.env` (на основе `.env.example`), поднимите Postgres и Redis, затем запустите:

```
python run.py
```

3. Откройте OpenAPI: http://localhost:8000/docs


## Переменные окружения

См. `.env.example`.

## Сидирование данных

Заполнить базу примерами:

```
source .venv/bin/activate
python -m app.main  # создаст таблицы (или просто запустите сервер один раз)
python scripts/seed.py
```

Скрипт добавит 6+ вакансий, 2–3 примерных PDF (в `uploads/`) и несколько демо‑откликов. Для очистки можно выполнить:

```
python scripts/clear_db.py
```

## Тестирование

Минимальные smoke‑тесты:

```
pip install -r requirements.txt
pytest -q
```

## Аутентификация и роли

- Вход администратора: POST /api/v1/admin/login с JSON {"email","password"}. В ответе приходит Bearer токен.
- Токен содержит subject вида user:<id> и claim role.
- Защищенные эндпоинты требуют роль admin.

Демо‑пользователи (после scripts/seed.py):
- admin@example.com / admin123 (role: admin)
- hr@example.com / hr123 (role: admin)

Создание вакансии (POST /api/v1/vacancies) теперь доступно только администратору, запись помечается created_by.