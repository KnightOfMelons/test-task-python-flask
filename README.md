# Тестовое задание Python Developer

## Описание проекта

Это API для управления пользователями. Предоставляет основные функции для создания, получения, обновления и удаления пользователей, а также позволяет анализировать статистику и прогнозировать активность пользователей. Проект использует Flask, SQLAlchemy, и другие библиотеки для работы с базой данных, валидации электронной почты и предоставления документации через Swagger.

## Цели проекта

- Реализовать REST API для управления пользователями.
- Предоставить функциональность для создания, получения, обновления и удаления пользователей.
- Реализовать прогнозирование активности пользователей на основе их данных.
- Разработать удобное API с документацией через Swagger для простоты использования и тестирования.

## Основные функции

- **POST /users**: Создание нового пользователя.
- **GET /users**: Получение списка пользователей с пагинацией.
- **GET /users/<int:user_id>**: Получение информации о пользователе по его ID.
- **PUT /users/<int:user_id>**: Обновление информации о пользователе.
- **DELETE /users/<int:user_id>**: Удаление пользователя по ID.
- **GET /users/last_7_days**: Количество пользователей, зарегистрированных за последние 7 дней.
- **GET /users/top_5_longest_names**: Топ-5 пользователей с самыми длинными именами.
- **GET /users/email_domain_proportion**: Доля пользователей с указанным доменом в электронной почте.
- **GET /users/statistics**: Комбинированная статистика: количество пользователей за последние 7 дней, топ-5 с длинными именами, доля пользователей по домену электронной почты.
- **GET /users/<int:user_id>/activity_probability**: Прогнозирование активности пользователя на основе его данных.

## Установка и запуск

Для того чтобы запустить проект на вашем компьютере, выполните следующие шаги:

### 1. Клонировать репозиторий

```bash
https://github.com/KnightOfMelons/test-task-python-flask.git
```

### 2. Установить зависимости

Убедитесь, что у вас установлен Python 3.11 или выше. Для установки зависимостей используйте `pip`:

```bash
pip install -r requirements.txt
```

### 3. Создать базу данных

Запустите приложение, чтобы создать базу данных и таблицы:

```bash
python app.py
```

### 4. Запустить сервер

После успешного выполнения вышеуказанных шагов сервер будет запущен по адресу `http://127.0.0.1:5000`. Вы можете использовать API с помощью HTTP-запросов или через Swagger UI, доступный по адресу `http://127.0.0.1:5000/swagger`.

## Документация Swagger

Документация API доступна по адресу:

```
http://127.0.0.1:5000/swagger
```

Swagger UI позволит вам тестировать все эндпоинты API без необходимости писать отдельные HTTP-запросы.

## Пример использования API

### Создание пользователя

```bash
POST /users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john.doe@example.com"
}
```

Ответ:
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john.doe@example.com",
    "registration_date": "2024-11-26T14:23:45",
    "last_active_date": null
  }
}
```

## Дополнительно

В проекте также присутствуют тесты. Для активации работы тестов необходимо их запустить:

```bash
python tests_app.py
```

## Требования

- Python 3.11 или выше
- Flask
- SQLAlchemy
- Flask-Migrate
- flask-swagger-ui
