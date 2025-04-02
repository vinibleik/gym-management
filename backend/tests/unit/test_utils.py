import json
import unittest
from dataclasses import InitVar, dataclass
from datetime import date
from typing import Any
from unittest.mock import MagicMock

from src.utils import (
    FieldsValidationError,
    ValidationError,
    validate_dataclass,
)


class TestPostInitValidation(unittest.TestCase):
    def test_call_post_init(self):
        @dataclass
        @validate_dataclass
        class TestUser:
            name: str
            last_name: InitVar[str]

            def __post_init__(self, last_name: str):
                self.name = self.name.upper() + last_name

        name = "user"
        last_name = "name"
        user = TestUser(name, last_name)
        self.assertEqual(
            name.upper() + last_name,
            user.name,
            "post_init_validation should call the __post_init__ method defined in class",
        )

    def test_raise_post_init(self):
        @dataclass
        @validate_dataclass
        class TestUser:
            def __post_init__(self):
                raise Exception()

        with self.assertRaisesRegex(
            ValidationError, "Error with post initializing class TestUser"
        ):
            TestUser()

    def test_call_validations(self):
        name_validation = MagicMock(return_value=True)
        age_validation = MagicMock(return_value=True)

        @dataclass
        @validate_dataclass
        class TestUser:
            name: str
            age: int

            def __validate_name__(*args):
                return name_validation(*args)

            def __validate_age__(*args):
                return age_validation(*args)

        name = "user"
        age = 23
        user = TestUser(name, age)

        name_validation.assert_called_once_with(user, name)
        age_validation.assert_called_once_with(user, age)

    def test_raise_one_validations_errors(self):
        @dataclass
        @validate_dataclass
        class TestUser:
            name: str

            def __validate_name__(*args):
                return False

        name = "user"
        errors = (
            {
                "field": "name",
                "value": "user",
                "msg": "Invalid value user for field name",
            },
        )

        with self.assertRaisesRegex(
            FieldsValidationError, json.dumps(errors)
        ) as e:
            TestUser(name)
        self.assertTupleEqual(
            e.exception.errors,
            errors,
        )

    def test_raise_multiple_validations_errors(self):
        @dataclass
        @validate_dataclass
        class TestUser:
            name: str
            age: int

            def __validate_name__(*args):
                return False

            def __validate_age__(*args):
                return False

        name = "user"
        age = 23

        errors = (
            {
                "field": "name",
                "value": "user",
                "msg": "Invalid value user for field name",
            },
            {
                "field": "age",
                "value": 23,
                "msg": "Invalid value 23 for field age",
            },
        )

        with self.assertRaisesRegex(
            FieldsValidationError, json.dumps(errors)
        ) as e:
            TestUser(name, age)
        self.assertTupleEqual(e.exception.errors, errors)

    def test_correct_parse_fields(self):
        @dataclass
        @validate_dataclass
        class Test:
            age: int
            birth: date

            def __post_init__(self) -> None:
                self.age = int(self.age)

            def __validate_birth__(self, birth: Any) -> bool:
                if isinstance(birth, date):
                    return True
                self.birth = date.fromisoformat(birth)
                return True

        birth = "1999-01-01"
        age = "23"
        t = Test(age, birth)  # type: ignore
        self.assertIsInstance(t.age, int)
        self.assertEqual(t.age, 23)
        self.assertIsInstance(t.birth, date)
        self.assertEqual(t.birth, date(year=1999, month=1, day=1))

    def test_capture_exception_on_validate(self):
        @dataclass
        @validate_dataclass
        class Test:
            birth: date

            def __validate_birth__(self, birth: Any) -> bool:
                if isinstance(birth, date):
                    return True
                self.birth = date.fromisoformat(birth)
                return True

        birth = "2026-00-00"
        with self.assertRaises(FieldsValidationError) as e:
            Test(birth)  # type: ignore

        self.assertEqual(len(e.exception.errors), 1)
        self.assertEqual(e.exception.errors[0]["field"], "birth")
        self.assertEqual(e.exception.errors[0]["value"], birth)
