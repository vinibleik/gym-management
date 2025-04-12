import unittest
from typing import Any
from unittest.mock import MagicMock

from src.utils.try_except import TryExcept


class MockError(Exception):
    mock: MagicMock

    def __init__(self, *args: object, **kwargs) -> None:
        self.mock = MagicMock()
        self.mock(*args, **kwargs)


class TestTryExcept(unittest.TestCase):
    tests: tuple[tuple[type[BaseException], tuple[Any, ...], dict], ...] = (
        (MockError, (), {}),
        (MockError, ("a", 23), {}),
        (MockError, (), {"name": "name", "age": 23}),
        (MockError, ("a", 23), {"name": "name", "age": 23}),
    )

    def test_should_init_correctly(self):
        t = TryExcept(Exception)
        self.assertIs(t.exc_type, Exception)
        self.assertDictEqual(t.exc_kwargs, {})
        self.assertTupleEqual(t.exc_args, ())
        t = TryExcept(Exception, "a", "b", 23)
        self.assertIs(t.exc_type, Exception)
        self.assertTupleEqual(t.exc_args, ("a", "b", 23))
        self.assertDictEqual(t.exc_kwargs, {})
        t = TryExcept(Exception, name="name", age=23)
        self.assertIs(t.exc_type, Exception)
        self.assertTupleEqual(t.exc_args, ())
        self.assertDictEqual(t.exc_kwargs, {"name": "name", "age": 23})
        t = TryExcept(Exception, "a", "b", 23, name="name", age=23)
        self.assertIs(t.exc_type, Exception)
        self.assertTupleEqual(t.exc_args, ("a", "b", 23))
        self.assertDictEqual(t.exc_kwargs, {"name": "name", "age": 23})

    def test_should_raise_the_exception_ctx_manager(self):
        for i, (exc, exc_args, exc_kwargs) in enumerate(self.tests):
            with (
                self.subTest(i=i),
                self.assertRaises(MockError) as e,
                TryExcept(exc, *exc_args, **exc_kwargs),
            ):
                raise Exception
            e.exception.mock.assert_called_once_with(*exc_args, **exc_kwargs)

    def test_should_passthrought_the_exception_ctx_manager(self):
        for i, (exc, exc_args, exc_kwargs) in enumerate(self.tests):
            with (
                self.subTest(i=i),
                self.assertRaises(MockError) as e,
                TryExcept(exc, *exc_args, **exc_kwargs),
            ):
                raise MockError("value", 99, gg="gg")
            e.exception.mock.assert_called_once_with("value", 99, gg="gg")

    def test_should_call_and_return_value_decorator(self):
        mock = MagicMock()
        mock.return_value = "return_value"
        args = ("name", 23)
        kwargs = {"name": "name", "age": 23}
        return_value = TryExcept(Exception)(mock)(
            "name", 23, name="name", age=23
        )
        self.assertEqual(return_value, "return_value")
        mock.assert_called_once_with(*args, **kwargs)

    def test_should_raise_the_exception_decorator(self):
        for i, (exc, exc_args, exc_kwargs) in enumerate(self.tests):
            mock = MagicMock()
            mock.side_effect = Exception()
            with (
                self.subTest(i=i),
                self.assertRaises(MockError) as e,
            ):
                TryExcept(exc, *exc_args, **exc_kwargs)(mock)(
                    *exc_args, **exc_kwargs
                )
            e.exception.mock.assert_called_once_with(*exc_args, **exc_kwargs)
            mock.assert_called_once_with(*exc_args, **exc_kwargs)

    def test_should_passthrought_the_exception_decorator(self):
        for i, (exc, exc_args, exc_kwargs) in enumerate(self.tests):
            mock = MagicMock()
            mock.side_effect = MockError(
                "error", 99, error="name", error_code=23
            )
            with (
                self.subTest(i=i),
                self.assertRaises(MockError) as e,
            ):
                TryExcept(exc, *exc_args, **exc_kwargs)(mock)(
                    *exc_args, **exc_kwargs
                )
            e.exception.mock.assert_called_once_with(
                "error", 99, error="name", error_code=23
            )
            mock.assert_called_once_with(*exc_args, **exc_kwargs)
