import unittest
from dataclasses import asdict
from datetime import UTC, date, datetime
from unittest.mock import patch

from src.models.user import BaseUser
from src.utils import ValidationError


class MockDate(date): ...


class TestBaseUser(unittest.TestCase):
    user: BaseUser

    def setUp(self) -> None:
        self.user = BaseUser(
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
                u = BaseUser(**self.user_dict)
                self.assertEqual(u.username, v)

    def test_should_raise_invalid_username(self):
        invalid_values = ["", 23, {}, [], datetime.now(UTC)]
        regex_err = f"{ValidationError.__name__}: Error while validating {BaseUser.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["username"] = v
                BaseUser(**self.user_dict)
            self.assertIn("username", e.exception.to_json())
            self.assertIn(str(v), e.exception.to_json())

    def test_should_validate_name(self):
        valid_values = ["name", "NAME", "username"]
        for i, v in enumerate(valid_values):
            with self.subTest(i=i):
                self.user_dict["name"] = v
                u = BaseUser(**self.user_dict)
                self.assertEqual(u.name, v)

    def test_should_raise_invalid_name(self):
        invalid_values = ["", 23, {}, [], datetime.now(UTC)]
        regex_err = f"{ValidationError.__name__}: Error while validating {BaseUser.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["name"] = v
                BaseUser(**self.user_dict)
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
                u = BaseUser(**self.user_dict)
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
        regex_err = f"{ValidationError.__name__}: Error while validating {BaseUser.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["date_of_birth"] = v
                BaseUser(**self.user_dict)
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
                u = BaseUser(**self.user_dict)
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
        regex_err = f"{ValidationError.__name__}: Error while validating {BaseUser.__name__}."
        for i, v in enumerate(invalid_values):
            with (
                self.subTest(i=i),
                self.assertRaisesRegex(ValidationError, regex_err) as e,
            ):
                self.user_dict["role"] = v
                BaseUser(**self.user_dict)
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
                u = BaseUser(**self.user_dict)
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
                u = BaseUser(**self.user_dict)
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
                u = BaseUser(**self.user_dict)
                self.assertEqual(u.age, age)
            i += 1
