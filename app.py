import logging
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_base.db'
db = SQLAlchemy(app)


class User(db.Model):
    """
    Модель пользователя

    Представляет собой пользователя с уникальным именем пользователя, электронной почтой,
    а также хранит дату регистрации

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        username (str): Имя пользователя, которое должно быть уникальным и обязательным.
        email (str): Электронная почта пользователя, которая также должна быть уникальной и обязательной.
        registration_date (datetime): Дата и время регистрации пользователя, по умолчанию устанавливается текущее время.

    Методы:
        json(): Возвращает словарь с данными пользователя для сериализации в формат JSON.
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def json(self):
        return {"id": self.id,
                "username": self.username,
                "email": self.email,
                "registration_date": self.registration_date}


with app.app_context():
    db.create_all()


def get_user_by_id(user_id):
    """
    Получает пользователя по его уникальному идентификатору.

    Аргументы:
        user_id (int): Уникальный идентификатор пользователя.

    Возвращает:
        User: Объект пользователя, если найден, иначе None.
    """
    try:
        return User.query.filter_by(id=user_id).first()
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return None


@app.route("/users", methods=["POST"])
def create_user():
    """
    Создает нового пользователя на основе данных, переданных в запросе.

    Ожидает получение JSON-данных с полями "username" и "email".

    Возвращает:
        Response: Ответ с кодом состояния 201 и информацией о созданном пользователе,
                  если запрос успешен, или ошибку 400 или 500 при возникновении ошибок.
    """
    try:
        data = request.get_json()

        if "email" not in data or "username" not in data:
            return make_response(jsonify({"message": "username and email are required"}), 400)

        try:
            validate_email(data["email"])
        except EmailNotValidError as e:
            return make_response(jsonify({"message": str(e)}), 400)

        new_user = User(username=data["username"],
                        email=data["email"])
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({"status": "success", "user": new_user.json()}), 201)
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


@app.route("/users", methods=["GET"])
def get_users():
    """
    Получает список пользователей с поддержкой пагинации.

    Параметры:
        - `page` (int): Номер страницы, по умолчанию 1.
        - `per_page` (int): Количество пользователей на одной странице, по умолчанию 10.

    Ожидает:
        Параметры запроса:
            - `page`: Номер страницы (по умолчанию 1).
            - `per_page`: Количество пользователей на странице (по умолчанию 10).

    Возвращает:
        Response: Ответ с кодом состояния 200 и JSON, содержащий:
            - `page`: Текущая страница.
            - `per_page`: Количество пользователей на странице.
            - `total`: Общее количество пользователей в базе данных.
            - `total_pages`: Общее количество страниц.
            - `users`: Список пользователей на текущей странице, представленных в формате JSON.

    В случае ошибки:
        Response: Ответ с кодом состояния 500 и сообщением об ошибке.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        users_paginated = User.query.paginate(page=page, per_page=per_page, error_out=False)

        return make_response(jsonify({
            "page": users_paginated.page,
            "per_page": users_paginated.per_page,
            "total": users_paginated.total,
            "total_pages": users_paginated.pages,
            "users": [user.json() for user in users_paginated.items]
        }), 200)
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return make_response(jsonify({"message": str(e)}), 500)


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Возвращает информацию о пользователе по его уникальному идентификатору.

    Аргументы:
        user_id (int): Уникальный идентификатор пользователя.

    Возвращает:
        Response: Ответ с кодом состояния 200 и данными пользователя в формате JSON,
                  или ошибку 404, если пользователь не найден.
    """
    try:
        user = get_user_by_id(user_id)
        if user:
            return make_response(jsonify({"user": user.json()}), 200)
        return make_response(jsonify({"message": "user not found"}), 404)
    except Exception as e:
        logging.error(f"Error fetching user {user_id}: {e}")
        return make_response(jsonify({"message": str(e)}), 500)


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Обновляет информацию о пользователе по его уникальному идентификатору.

    Аргументы:
        user_id (int): Уникальный идентификатор пользователя.

    Ожидает получение JSON-данных с возможными полями "username", "email", "registration_date".

    Возвращает:
        Response: Ответ с кодом состояния 200 и сообщением о том, что пользователь был обновлен,
                  или ошибку 404, если пользователь не найден.
    """
    try:
        user = get_user_by_id(user_id)
        if user:
            data = request.get_json()

            if "username" in data:
                user.username = data["username"]
            if "email" in data:
                user.email = data["email"]
            if "registration_date" in data:
                user.registration_date = data["registration_date"]

            db.session.commit()
            return make_response(jsonify({"message": "user updated"}), 200)
        return make_response(jsonify({"message": "user not found"}), 404)
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Удаляет пользователя по его уникальному идентификатору.

    Аргументы:
        user_id (int): Уникальный идентификатор пользователя.

    Возвращает:
        Response: Ответ с кодом состояния 200 и сообщением о том, что пользователь был удален,
                  или ошибку 404, если пользователь не найден.
    """
    try:
        user = get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({"message": "user deleted"}), 200)
        return make_response(jsonify({"message": "user not found"}), 404)
    except Exception as e:
        return make_response(jsonify({"message": str(e)}), 500)


if __name__ == "__main__":
    """
    Запускает приложение Flask на локальном сервере с включенным режимом отладки.
    """
    app.run(debug=True)