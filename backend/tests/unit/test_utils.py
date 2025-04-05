import json
import unittest
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

from src.utils import FieldError, ValidationError, validate_dataclass


class TestFieldError(unittest.TestCase):
    error_no_reason: FieldError
    error_reason: FieldError
    name = "name"
    value = "value"
    reason = "reason"

    def setUp(self) -> None:
        self.error_no_reason = FieldError(self.name, self.value)
        self.error_reason = FieldError(self.name, self.value, self.reason)

    def test_field_error_init(self):
        f = FieldError(self.name, self.value)
        self.assertEqual(f.name, self.name)
        self.assertEqual(f.value, self.value)
        self.assertEqual(f.reason, None)

        f = FieldError(name=self.name, value=self.value, reason=self.reason)
        self.assertEqual(f.name, self.name)
        self.assertEqual(f.value, self.value)
        self.assertEqual(f.reason, self.reason)

    def test_repr_with_no_reason(self):
        self.assertEqual(
            repr(self.error_no_reason),
            f"{FieldError.__name__}({self.name}, {self.value})",
        )

    def test_repr_with_reason(self):
        self.assertEqual(
            repr(self.error_reason),
            f'{FieldError.__name__}({self.name}, {self.value}, "{self.reason}")',
        )

    def test_str_with_no_reason(self):
        self.assertEqual(
            str(self.error_no_reason),
            f"{FieldError.__name__}: Invalid value <{self.value}> for field <{self.name}>",
        )

    def test_str_with_reason(self):
        self.assertEqual(
            str(self.error_reason),
            f"{FieldError.__name__}: Invalid value <{self.value}> for field <{self.name}>\n  Reason: {self.reason}",
        )

    def test_should_return_dict_with_reason(self):
        self.assertEqual(
            self.error_reason.to_dict(),
            {"name": self.name, "value": self.value, "reason": self.reason},
        )

    def test_should_return_dict_with_no_reason(self):
        self.assertEqual(
            self.error_no_reason.to_dict(),
            {"name": self.name, "value": self.value},
        )

    def test_should_return_json_str_with_reason(self):
        self.assertEqual(
            self.error_reason.to_json(),
            json.dumps(
                {"name": self.name, "value": self.value, "reason": self.reason}
            ),
        )

    def test_should_return_json_str_with_no_reason(self):
        self.assertEqual(
            self.error_no_reason.to_json(),
            json.dumps({"name": self.name, "value": self.value}),
        )


class TestValidateError(unittest.TestCase):
    error_no_reason: FieldError
    error_reason: FieldError
    errors_tests: list[list[FieldError]]
    name = "name"
    value = "value"
    reason = "reason"
    cls_name = "cls_name"

    def setUp(self) -> None:
        self.error_no_reason = FieldError(self.name, self.value)
        self.error_reason = FieldError(self.name, self.value, self.reason)
        self.errors_tests = [
            [self.error_reason],
            [self.error_reason, self.error_no_reason],
        ]

    def test_field_error_init(self):
        v = ValidationError(
            self.cls_name, [self.error_reason, self.error_no_reason]
        )
        self.assertEqual(v.cls_name, self.cls_name)
        self.assertListEqual(
            v.errors, [self.error_reason, self.error_no_reason]
        )

    def test_validate_to_dict(self):
        for i, errors in enumerate(self.errors_tests):
            with self.subTest(i=i):
                v = ValidationError(self.cls_name, errors)
                self.assertDictEqual(
                    v.to_dict(),
                    {
                        "cls_name": self.cls_name,
                        "errors": [e.to_dict() for e in errors],
                    },
                )

    def test_validate_to_json(self):
        for i, errors in enumerate(self.errors_tests):
            with self.subTest(i=i):
                v = ValidationError(self.cls_name, errors)
                self.assertEqual(
                    v.to_json(),
                    json.dumps(
                        {
                            "cls_name": self.cls_name,
                            "errors": [e.to_dict() for e in errors],
                        }
                    ),
                )

    def test_validate_to_str(self):
        for i, errors in enumerate(self.errors_tests):
            v = ValidationError(self.cls_name, errors)
            expected = f"{ValidationError.__name__}: Error while validating {self.cls_name}. The following errors were found:\n{'\n'.join(map(str, errors))}"
            with self.subTest(i=i):
                self.assertEqual(str(v), expected)

    def test_validate_to_repr(self):
        for i, errors in enumerate(self.errors_tests):
            v = ValidationError(self.cls_name, errors)
            expected = f'{ValidationError.__name__}(\n  "{self.cls_name}",\n  [\n    {",\n    ".join(map(repr, errors))}\n  ]\n)'
            with self.subTest(i=i):
                self.assertEqual(repr(v), expected)


class TestValidateDataclass(unittest.TestCase):
    def test_should_not_throw_error_for_not_dataclass(self):
        with self.assertRaisesRegex(
            ValueError, "class Person must be a dataclass"
        ):

            @validate_dataclass
            class Person: ...

        with self.assertRaisesRegex(
            ValueError, "class Student must be a dataclass"
        ):

            @validate_dataclass
            class Student: ...

        @validate_dataclass
        @dataclass
        class ShouldWork: ...

    def test_should_run_fields_validators(self):
        name_validation = MagicMock(return_value=True)
        age_validation = MagicMock(return_value=True)

        @validate_dataclass
        @dataclass
        class Person:
            name: str
            age: int

            def __validate_name__(*args, **kwargs):
                return name_validation(*args, **kwargs)

            def __validate_age__(*args, **kwargs):
                return age_validation(*args, **kwargs)

        name = "user"
        age = 23
        user = Person(name, age)

        name_validation.assert_called_once_with(user, name="name", value=name)
        age_validation.assert_called_once_with(user, name="age", value=age)

    def test_should_run_fields_validators_inheritance(self):
        name_validation = MagicMock(return_value=True)
        person_age_validation = MagicMock(return_value=True)
        student_age_validation = MagicMock(return_value=True)
        id_validation = MagicMock(return_value=True)

        @validate_dataclass
        @dataclass
        class Person:
            name: str
            age: int

            def __validate_name__(*args, **kwargs):
                return name_validation(*args, **kwargs)

            def __validate_age__(*args, **kwargs):
                return person_age_validation(*args, **kwargs)

        @validate_dataclass
        @dataclass
        class Student(Person):
            id: str

            def __validate_age__(*args, **kwargs):
                return student_age_validation(*args, **kwargs)

            def __validate_id__(*args, **kwargs):
                return id_validation(*args, **kwargs)

        name = "user"
        age = 23
        _id = "id"
        user = Student(name, age, _id)

        name_validation.assert_called_once_with(user, name="name", value=name)
        person_age_validation.assert_not_called()
        student_age_validation.assert_called_once_with(
            user, name="age", value=age
        )
        id_validation.assert_called_once_with(user, name="id", value=_id)

    def test_should_run_fields_validators_inheritance_and_init(self):
        name_validation = MagicMock(return_value=True)
        person_age_validation = MagicMock(return_value=True)
        student_age_validation = MagicMock(return_value=True)
        id_validation = MagicMock(return_value=True)

        @validate_dataclass
        @dataclass
        class Person:
            name: str
            age: int

            def __validate_name__(*args, **kwargs):
                return name_validation(*args, **kwargs)

            def __validate_age__(*args, **kwargs):
                return person_age_validation(*args, **kwargs)

        @validate_dataclass
        @dataclass
        class Student(Person):
            id: str

            def __init__(self, _id, name, age) -> None:
                self.id = age
                self.name = _id
                self.age = name

            def __validate_age__(*args, **kwargs):
                return student_age_validation(*args, **kwargs)

            def __validate_id__(*args, **kwargs):
                return id_validation(*args, **kwargs)

        name = "user"
        age = 23
        _id = "id"
        s = Student(_id=_id, name=name, age=age)

        self.assertEqual(s.id, age)
        self.assertEqual(s.name, _id)
        self.assertEqual(s.age, name)
        name_validation.assert_called_once_with(s, name="name", value=_id)
        person_age_validation.assert_not_called()
        student_age_validation.assert_called_once_with(
            s, name="age", value=name
        )
        id_validation.assert_called_once_with(s, name="id", value=age)

    def test_should_throw_error_for_failed_validator(self):
        @validate_dataclass
        @dataclass
        class Person:
            name: str

            def __validate_name__(self, name: str, value: str) -> bool:
                return False

        with self.assertRaisesRegex(
            ValidationError,
            f"{ValidationError.__name__}: Error while validating {Person.__name__}",
        ) as e:
            Person("")

        exc = e.exception
        self.assertEqual(exc.cls_name, Person.__name__)
        self.assertEqual(len(exc.errors), 1)
        name = exc.errors[0]
        self.assertEqual(name.to_json(), FieldError("name", "").to_json())

    def test_should_throw_error_for_failed_validator_inhertance(self):
        name = "name"
        age = 23

        @validate_dataclass
        @dataclass
        class Person:
            name: str

            def __validate_name__(self, name: str, value: str) -> bool:
                return False

        @validate_dataclass
        @dataclass
        class Student(Person):
            def __validate_name__(self, name: str, value: str) -> bool:
                return True

        Student(name)

        @validate_dataclass
        @dataclass
        class Employee(Person):
            age: int

            def __validate_age__(self, name: str, value: int) -> bool:
                return False

        with self.assertRaisesRegex(
            ValidationError,
            f"{ValidationError.__name__}: Error while validating {Employee.__name__}",
        ) as e:
            Employee(name, age)

        exc = e.exception
        self.assertEqual(exc.cls_name, Employee.__name__)
        self.assertEqual(len(exc.errors), 2)
        name_error, age_error = exc.errors
        self.assertEqual(
            name_error.to_json(), FieldError("name", name).to_json()
        )
        self.assertEqual(age_error.to_json(), FieldError("age", age).to_json())

    def test_should_throw_error_with_custom_errors(self):
        name = "name"
        name_error_msg = "name should not be empty"
        error_name = FieldError("name", name, name_error_msg)
        age = 23
        age_error_msg = "age should not be 23"
        error_age = FieldError("age", age, age_error_msg)

        @validate_dataclass
        @dataclass
        class Person:
            name: str

            def __validate_name__(self, name: str, value: str) -> bool:
                raise error_name

        @validate_dataclass
        @dataclass
        class Student(Person):
            age: int

            def __validate_age__(self, name: str, value: Any) -> bool:
                raise error_age

        with self.assertRaisesRegex(
            ValidationError,
            f"{ValidationError.__name__}: Error while validating {Student.__name__}",
        ) as e:
            Student(name, age)

        exc = e.exception
        self.assertEqual(exc.cls_name, Student.__name__)
        errors = exc.errors
        self.assertEqual(len(errors), 2)
        name_err, age_err = errors
        self.assertEqual(name_err.to_json(), error_name.to_json())
        self.assertEqual(age_err.to_json(), error_age.to_json())

        @validate_dataclass
        @dataclass
        class Employee(Student):
            age: int

            def __validate_age__(self, name: str, value: Any) -> bool:
                return True

        with self.assertRaisesRegex(
            ValidationError,
            f"{ValidationError.__name__}: Error while validating {Employee.__name__}",
        ) as e:
            Employee(name, age)

        exc = e.exception
        self.assertEqual(exc.cls_name, Employee.__name__)
        errors = exc.errors
        self.assertEqual(len(errors), 1)
        name_err = errors[0]
        self.assertEqual(name_err.to_json(), error_name.to_json())

        @validate_dataclass
        @dataclass
        class Chef(Employee):
            age: int

            def __validate_name__(self, name: str, value: str) -> bool:
                return True

            def __validate_age__(self, name: str, value: Any) -> bool:
                raise error_age

        with self.assertRaisesRegex(
            ValidationError,
            f"{ValidationError.__name__}: Error while validating {Chef.__name__}",
        ) as e:
            Chef(name, age)

        exc = e.exception
        self.assertEqual(exc.cls_name, Chef.__name__)
        errors = exc.errors
        self.assertEqual(len(errors), 1)
        age_err = errors[0]
        self.assertEqual(age_err.to_json(), error_age.to_json())

        @validate_dataclass
        @dataclass
        class Boss(Chef):
            def __validate_name__(self, name: str, value: str) -> bool:
                return True

            def __validate_age__(self, name: str, value: Any) -> bool:
                return True

        Boss("", 23)
