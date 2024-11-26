import os
import unittest
from app import app, db, User
from datetime import datetime, timedelta


class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Создает тестовый клиент и тестовую базу данных."""
        app.config['TESTING'] = True

        # Указываем путь к тестовой базе данных
        test_db_path = os.path.join(os.path.dirname(__file__), "test_database", "test_app.db")
        os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///tests/{test_db_path}"

        cls.client = app.test_client()

        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Удаляет тестовую базу данных."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

        # Удаляем тестовую базу данных и папку
        test_db_path = os.path.join(os.path.dirname(__file__), "test_database", "test_app.db")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(os.path.dirname(test_db_path)):
            os.rmdir(os.path.dirname(test_db_path))

    def setUp(self):
        """Добавляет тестовые данные в базу перед каждым тестом"""
        with app.app_context():
            db.drop_all()
            db.create_all()

            user1 = User(username="Alice", email="alice@mail.ru", registration_date=datetime.utcnow())
            user2 = User(username="Bob", email="bob@gmail.com", registration_date=datetime.utcnow() - timedelta(days=3))
            user3 = User(username="Charlie", email="charlie@yahoo.com",
                         registration_date=datetime.utcnow() - timedelta(days=10))
            db.session.add_all([user1, user2, user3])
            db.session.commit()

    def tearDown(self):
        """Очищает базу данных после каждого теста."""
        with app.app_context():
            db.drop_all()

    def test_create_user(self):
        """Тестирует создание нового пользователя."""
        response = self.client.post('/users', json={
            "username": "David",
            "email": "david@mail.ru"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("status", response.json)
        self.assertEqual(response.json["status"], "success")

    def test_create_user_invalid_email(self):
        """Тестирует создание пользователя с некорректным email."""
        response = self.client.post('/users', json={
            "username": "Eve",
            "email": "not-an-email"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json)

    def test_get_users(self):
        """Тестирует получение списка пользователей."""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.json)
        self.assertGreaterEqual(len(response.json["users"]), 1)

    def test_get_user_by_id(self):
        """Тестирует получение пользователя по ID."""
        with app.app_context():
            user = User.query.first()
        response = self.client.get(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("user", response.json)

    def test_get_user_not_found(self):
        """Тестирует запрос пользователя с несуществующим ID."""
        response = self.client.get('/users/999')
        self.assertEqual(response.status_code, 404)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "user not found")

    def test_update_user(self):
        """Тестирует обновление данных пользователя."""
        with app.app_context():
            user = User.query.first()
        response = self.client.put(f'/users/{user.id}', json={
            "username": "UpdatedAlice"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "user updated")

    def test_delete_user(self):
        """Тестирует удаление пользователя."""
        with app.app_context():
            user = User.query.first()
        response = self.client.delete(f'/users/{user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "user deleted")

    def test_last_7_days_users(self):
        """Тестирует получение количества пользователей за последние 7 дней."""
        response = self.client.get('/users/last_7_days')
        self.assertEqual(response.status_code, 200)
        self.assertIn("users_count_7_days", response.json)

    def test_top_5_longest_names(self):
        """Тестирует получение топ-5 пользователей с самыми длинными именами."""
        response = self.client.get('/users/top_5_longest_names')
        self.assertEqual(response.status_code, 200)
        self.assertIn("top_5_longest_names", response.json)

    def test_email_domain_proportion(self):
        """Тестирует получение пропорции пользователей с определенным доменом."""
        response = self.client.get('/users/email_domain_proportion?domain=mail.ru')
        self.assertEqual(response.status_code, 200)
        self.assertIn("domain", response.json)
        self.assertIn("total_users", response.json)
        self.assertIn("domain_users", response.json)
        self.assertIn("proportions", response.json)
        self.assertEqual(response.json["domain"], "mail.ru")

    def test_activity_probability(self):
        """Тестирует расчет вероятности активности пользователя."""
        with app.app_context():
            user = User.query.first()
        response = self.client.get(f'/users/{user.id}/activity_probability')
        self.assertEqual(response.status_code, 200)
        self.assertIn("activity_probability", response.json)

    def test_combined_statistics(self):
        """Тестирует получение комбинированной статистики."""
        response = self.client.get('/users/statistics')
        self.assertEqual(response.status_code, 200)
        self.assertIn("user_count_7_days", response.json)
        self.assertIn("top_5_longest_names", response.json)
        self.assertIn("email_domain_proportion", response.json)


if __name__ == '__main__':
    unittest.main()
