import unittest
from dataclasses import asdict
from datetime import UTC, date, datetime
from typing import Any
from unittest.mock import patch

from src.models.user import User, UserBase, UserCreate, UserCreateBody, UserInDB
from src.utils.dataclass import ValidationError


class MockDate(date): ...


class TestBaseUser(unittest.TestCase):
    user: UserBase

    def setUp(self) -> None:
        self.user = UserBase(
            username="username",
            name="name",
            date_of_birth=datetime.now(tz=UTC).date(),
            role="staff",
        )
        self.user_dict = asdict(self.user)

    def test_should_validate_username(self):
        valid_values = ["username", "user", "baseuser", "43214312"]
        for i, v in enumerate(valid_values):
            with self.subTest(i=i):
                self.user_dict["username"] = v
                u = UserBase(**self.user_dict)
                self.assertEqual(u.username, v)

    def test_should_raise_invalid_username(self):
        invalid_values = ["", 23, {}, [], datetime.now(UTC)]
        regex_err = f"{ValidationError.__name__}: Error while validating {UserBase.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["username"] = v
                UserBase(**self.user_dict)
            self.assertIn("username", e.exception.to_json())
            self.assertIn(str(v), e.exception.to_json())

    def test_should_validate_name(self):
        valid_values = ["name", "NAME", "username"]
        for i, v in enumerate(valid_values):
            with self.subTest(i=i):
                self.user_dict["name"] = v
                u = UserBase(**self.user_dict)
                self.assertEqual(u.name, v)

    def test_should_raise_invalid_name(self):
        invalid_values = ["", 23, {}, [], datetime.now(UTC)]
        regex_err = f"{ValidationError.__name__}: Error while validating {UserBase.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["name"] = v
                UserBase(**self.user_dict)
            self.assertIn("name", e.exception.to_json())
            self.assertIn(str(v), e.exception.to_json())

    def test_should_validate_date_of_birth(self):
        date_today = date.today()
        datetime_now = datetime.now(UTC)
        timestamp = 4321413434
        valid_values = [
            (date_today, date_today),
            (datetime_now, datetime_now.date()),
            (timestamp, datetime.fromtimestamp(timestamp).date()),
            ("2011-11-04", datetime.fromisoformat("2011-11-04").date()),
            ("20111104", datetime.fromisoformat("20111104").date()),
            (
                "2011-11-04T00:05:23",
                datetime.fromisoformat("2011-11-04T00:05:23").date(),
            ),
            (
                "2011-11-04T00:05:23Z",
                datetime.fromisoformat("2011-11-04T00:05:23Z").date(),
            ),
            (
                "20111104T000523",
                datetime.fromisoformat("20111104T000523").date(),
            ),
            (
                "2011-W01-2T00:05:23.283",
                datetime.fromisoformat("2011-W01-2T00:05:23.283").date(),
            ),
            (
                "2011-11-04 00:05:23.283",
                datetime.fromisoformat("2011-11-04 00:05:23.283").date(),
            ),
            (
                "2011-11-04 00:05:23.283+00:00",
                datetime.fromisoformat("2011-11-04 00:05:23.283+00:00").date(),
            ),
            (
                "2011-11-04T00:05:23+04:00",
                datetime.fromisoformat("2011-11-04T00:05:23+04:00").date(),
            ),
        ]
        for i, (value, expected) in enumerate(valid_values):
            with self.subTest(i=i):
                self.user_dict["date_of_birth"] = value
                u = UserBase(**self.user_dict)
                self.assertEqual(u.date_of_birth, expected)

    def test_should_raise_invalid_date_of_birth(self):
        invalid_values = [
            "",
            {},
            [],
            "9999-99-99",
            "99999999",
            "99-99-99",
            "99-99-9999",
            "2011-11-04T99:05:23+04:00",
            "2011-11-04T:05:23+04:00",
        ]
        regex_err = f"{ValidationError.__name__}: Error while validating {UserBase.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["date_of_birth"] = v
                UserBase(**self.user_dict)
            self.assertIn("date", e.exception.to_json())
            self.assertIn(str(v), e.exception.to_json())

    def test_should_validate_role(self):
        valid_values = {
            "staff",
            "personal",
            "student",
            "STAFF",
            "PERSONAL",
            "STUDENT",
        }
        for i, v in enumerate(valid_values):
            with self.subTest(i=i):
                self.user_dict["role"] = v
                u = UserBase(**self.user_dict)
                self.assertEqual(u.role, v.lower())

    def test_should_raise_invalid_role(self):
        invalid_values = [
            "",
            {},
            [],
            "9999-99-99",
            "99999999",
            "99-99-99",
            "99-99-9999",
            "2011-11-04T99:05:23+04:00",
            "2011-11-04T:05:23+04:00",
            "staffing",
            "teacher",
            "aluno",
        ]
        regex_err = f"{ValidationError.__name__}: Error while validating {UserBase.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["role"] = v
                UserBase(**self.user_dict)
            self.assertIn("role", e.exception.to_json())
            self.assertIn(str(v), e.exception.to_json())

    @patch("src.models.user.date", MockDate)
    def test_should_return_the_correct_age(self):
        tests = (
            (MockDate(2016, 2, 28), 4),
            (MockDate(2016, 2, 29), 4),
            (MockDate(2016, 3, 1), 4),
            (MockDate(2016, 6, 5), 4),
            (MockDate(2016, 6, 6), 4),
            (MockDate(2016, 6, 7), 3),
        )
        i = 0
        MockDate.today = classmethod(lambda _: MockDate(2020, 6, 6))  # type: ignore
        for born, age in tests:
            self.user_dict["date_of_birth"] = born
            with self.subTest(i=i):
                u = UserBase(**self.user_dict)
                self.assertEqual(u.age, age)
            i += 1
        tests = (
            (MockDate(2016, 2, 28), 4),
            (MockDate(2016, 2, 29), 3),
            (MockDate(2016, 3, 1), 3),
            (MockDate(2016, 6, 5), 3),
            (MockDate(2016, 6, 6), 3),
            (MockDate(2016, 6, 7), 3),
        )
        MockDate.today = classmethod(lambda _: date(2020, 2, 28))  # type: ignore
        for born, age in tests:
            self.user_dict["date_of_birth"] = born
            with self.subTest(i=i):
                u = UserBase(**self.user_dict)
                self.assertEqual(u.age, age)
            i += 1
        tests = (
            (MockDate(2016, 2, 28), 4),
            (MockDate(2016, 2, 29), 4),
            (MockDate(2016, 3, 1), 3),
            (MockDate(2016, 6, 5), 3),
            (MockDate(2016, 6, 6), 3),
            (MockDate(2016, 6, 7), 3),
        )
        MockDate.today = classmethod(lambda _: date(2020, 2, 29))  # type: ignore
        for born, age in tests:
            self.user_dict["date_of_birth"] = born
            with self.subTest(i=i):
                u = UserBase(**self.user_dict)
                self.assertEqual(u.age, age)
            i += 1

    def test_should_transform_date_to_iso_format(self):
        tests = (
            (date(1990, 9, 23), "1990-09-23"),
            (date(2000, 12, 1), "2000-12-01"),
            (date(1950, 5, 6), "1950-05-06"),
            ("2020-11-11", "2020-11-11"),
        )
        for i, (born, expected) in enumerate(tests):
            self.user_dict["date_of_birth"] = born
            with self.subTest(i=i):
                u = UserBase(**self.user_dict)
                self.assertDictEqual(
                    u.to_dict(transform=True),
                    {**self.user_dict, "date_of_birth": expected},
                )

            i += 1


class TestUserCreateBody(unittest.TestCase):
    user: UserCreateBody
    user_dict: dict[str, Any]

    def setUp(self) -> None:
        self.user = UserCreateBody(
            username="username",
            name="name",
            date_of_birth=datetime.now(tz=UTC).date(),
            role="staff",
            password="password",
        )
        self.user_dict = asdict(self.user)

    def test_should_validate_password(self):
        valid_values = ["password", "12345678"]
        for i, v in enumerate(valid_values):
            with self.subTest(i=i):
                self.user_dict["password"] = v
                u = UserCreateBody(**self.user_dict)
                self.assertEqual(u.password, v)

    def test_should_raise_invalid_password(self):
        invalid_values = [
            "",
            "passwd",
            "1234567",
            23,
            {},
            [],
            datetime.now(UTC),
        ]
        regex_err = f"{ValidationError.__name__}: Error while validating {UserCreateBody.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["password"] = v
                UserCreateBody(**self.user_dict)
            self.assertIn("password", e.exception.to_json())
            self.assertIn(str(v), e.exception.to_json())


class TestUser(unittest.TestCase):
    def test_should_convert_a_user_create(self):
        user_dict = {
            "id": 0,
            "username": "username",
            "name": "name",
            "role": "staff",
            "date_of_birth": date(1990, 9, 9),
        }
        user = UserInDB(**user_dict, password_hash="password_hash")  # type: ignore
        self.assertDictEqual(User.from_db_model(user).to_dict(), user_dict)


class TestUserInDb(unittest.TestCase):
    def test_should_convert_a_user_create(self):
        user_dict = {
            "username": "username",
            "name": "name",
            "password_hash": "password_hash",
            "role": "staff",
            "date_of_birth": "1990-09-09",
        }
        user = UserInDB(**user_dict, id=0)  # type: ignore
        user_create = UserCreate(**user_dict)  # type: ignore
        self.assertDictEqual(
            UserInDB.from_user_create(0, user_create).to_dict(), user.to_dict()
        )
