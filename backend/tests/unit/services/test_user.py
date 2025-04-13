import unittest
from datetime import date
from unittest.mock import MagicMock, call

from src.models.user import UserCreate, UserInDB
from src.repositories.user import InMemoryUserRepository, UserRepository
from src.services.user import (
    UserService,
    UserServiceError,
    UserServiceValidationError,
)


class MockRepository(UserRepository):
    repo: InMemoryUserRepository
    update_mock: MagicMock
    create_mock: MagicMock
    delete_mock: MagicMock
    find_all_mock: MagicMock
    find_by_id_mock: MagicMock

    def __init__(
        self, side_effect: type[BaseException] | BaseException | None = None
    ) -> None:
        self.repo = InMemoryUserRepository()
        self.update_mock = MagicMock(
            side_effect=side_effect or self.repo.update
        )
        self.delete_mock = MagicMock(
            side_effect=side_effect or self.repo.delete
        )
        self.find_all_mock = MagicMock(
            side_effect=side_effect or self.repo.find_all
        )
        self.find_by_id_mock = MagicMock(
            side_effect=side_effect or self.repo.find_by_id
        )
        self.create_mock = MagicMock(
            side_effect=side_effect or self.repo.create
        )

    def create(self, *args, **kwargs) -> UserInDB:
        return self.create_mock(*args, **kwargs)

    def update(self, *args, **kwargs) -> UserInDB | None:
        return self.update_mock(*args, **kwargs)

    def delete(self, *args, **kwargs) -> UserInDB | None:
        return self.delete_mock(*args, **kwargs)

    def find_all(self, *args, **kwargs) -> list[UserInDB]:
        return self.find_all_mock(*args, **kwargs)

    def find_by_id(self, *args, **kwargs) -> UserInDB | None:
        return self.find_by_id_mock(*args, **kwargs)


class TestUserService(unittest.TestCase):
    mock_repo: MockRepository
    mock_repo_exc: MockRepository

    def setUp(self) -> None:
        self.mock_repo = MockRepository()
        self.mock_repo_exc = MockRepository(Exception)
        self.service = UserService(self.mock_repo)
        self.servce_exc = UserService(self.mock_repo_exc)
        self.users: list[UserInDB] = []
        self.user_create_0 = UserCreate(
            name="name 0",
            password_hash="hash",
            role="staff",
            username="username 0",
            date_of_birth=date(1990, 9, 9),
        )
        self.user_create_1 = UserCreate(
            name="name 1",
            password_hash="hash",
            role="personal",
            username="username 1",
            date_of_birth=date(1990, 9, 9),
        )

    def _create_users(self) -> None:
        self.users.append(self.service.create_user(self.user_create_0))
        self.users.append(self.service.create_user(self.user_create_1))

    def test_should_create_user(self):
        user_create_0 = UserCreate(
            name="name 0",
            password_hash="hash",
            role="staff",
            username="username 0",
            date_of_birth=date(1990, 9, 9),
        )
        user_create_1 = UserCreate(
            name="name 1",
            password_hash="hash",
            role="personal",
            username="username 1",
            date_of_birth=date(1990, 9, 9),
        )
        users: list[UserInDB] = []
        users.append(self.service.create_user(user_create_0))
        users.append(self.service.create_user(user_create_1))
        self.mock_repo.create_mock.has_call(
            [call(user_create_0), call(user_create_1)]
        )
        self.assertDictEqual(
            self.mock_repo.repo._data, {u.id: u for u in users}
        )

    def test_should_validate_data_on_create(self):
        tests = (
            {},
            {
                "name": "name 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "staff",
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
            },
            {
                "username": "",
                "name": "name 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "role",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "staff",
                "date_of_birth": "",
                "password_hash": "password",
            },
        )
        for i, t in enumerate(tests):
            with (
                self.subTest(i=i),
                self.assertRaises(UserServiceValidationError),
            ):
                self.service.create_user(t)

    def test_should_raise_correct_error_on_create(self):
        with self.assertRaises(UserServiceError):
            valid_user = UserCreate(
                name="name 0",
                password_hash="hash",
                role="staff",
                username="username 0",
                date_of_birth=date(1990, 9, 9),
            )
            self.servce_exc.create_user(valid_user)

    def test_should_find_all(self):
        self.assertListEqual(self.service.find_all_users(), [])
        self.mock_repo.find_all_mock.assert_called_once_with()
        self._create_users()
        self.assertListEqual(self.service.find_all_users(), self.users)

    def test_should_raise_correct_error_on_find_all(self):
        with self.assertRaises(UserServiceError):
            self.assertListEqual(self.servce_exc.find_all_users(), [])

    def test_should_find_by_id_return_none(self):
        self.assertIsNone(self.service.find_user_by_id(4321))

    def test_should_find_by_id_return_user(self):
        self._create_users()
        self.assertEqual(
            self.service.find_user_by_id(self.users[0].id), self.users[0]
        )
        self.assertEqual(
            self.service.find_user_by_id(self.users[1].id), self.users[1]
        )

    def test_should_raise_correct_error_on_find_by_id(self):
        with self.assertRaises(UserServiceError):
            self.servce_exc.find_user_by_id(0)

    def test_should_delete_users_by_id_return_none(self):
        self.assertIsNone(self.service.delete_user_by_id(0))

    def test_should_delete_users_by_id(self):
        self._create_users()
        for u in self.users:
            with self.subTest(i=u.id):
                self.assertEqual(self.service.delete_user_by_id(u.id), u)

    def test_should_raise_correct_error_on_delete(self):
        with self.assertRaises(UserServiceError):
            self.servce_exc.delete_user_by_id(0)

    def test_should_validate_data_on_update(self):
        tests = (
            {},
            {
                "name": "name 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "staff",
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
            },
            {
                "username": "",
                "name": "name 0",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "",
                "role": "staff",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "role",
                "date_of_birth": date(1999, 9, 9),
                "password_hash": "password",
            },
            {
                "username": "username 0",
                "name": "name 0",
                "role": "staff",
                "date_of_birth": "",
                "password_hash": "password",
            },
        )
        for i, t in enumerate(tests):
            with (
                self.subTest(i=i),
                self.assertRaises(UserServiceValidationError),
            ):
                self.service.update_user(0, t)

    def test_should_update_return_none(self):
        user_update = UserCreate(
            name="updated_name",
            password_hash="updated_password",
            role="student",
            username="updated_username",
            date_of_birth=date(2010, 10, 10),
        )
        self.assertIsNone(self.service.update_user(99, user_update))

    def test_should_update_user(self):
        user_update = UserCreate(
            name="updated_name",
            password_hash="updated_password",
            role="student",
            username="updated_username",
            date_of_birth=date(2010, 10, 10),
        )
        self._create_users()
        updated_user = self.service.update_user(self.users[0].id, user_update)
        self.assertEqual(
            updated_user, UserInDB(id=self.users[0].id, **user_update.to_dict())
        )

    def test_should_raise_correct_error_on_update(self):
        user_update = UserCreate(
            name="updated_name",
            password_hash="updated_password",
            role="student",
            username="updated_username",
            date_of_birth=date(2010, 10, 10),
        )
        self._create_users()
        with self.assertRaises(UserServiceError):
            self.servce_exc.update_user(self.users[0].id, user_update)
