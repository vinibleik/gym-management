import functools
from collections.abc import Callable
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Any


class TryExcept(AbstractContextManager):
    """Class to capture exceptions and raise the provided exception.

    This class takes an exception and optional arguments to instantiate
    the provided exception, then can be used as a decorator or context manager.

    The decorator (or context manager) will capture any exception that
    was raised. If the raised exception is an instance of the provided
    exception, then it's re-raised. Otherwise, the provided exception will
    be raised with the supplied arguments.

    Attributes:
        exc_type: Exception to raise in place of other exceptions.
        *exc_args: Positional arguments to pass to "exc_type" instantiation.
        **exc_kwargs: Keyword arguments to pass to "exc_type" instantiation.
    """

    exc_type: type[BaseException]
    exc_args: tuple[Any, ...]
    exc_kwargs: dict[str, Any]

    def __init__(
        self, exc_type: type[BaseException], *exc_args, **exc_kwargs
    ) -> None:
        """
        Args:
            exc_type: Exception to raise in place of the others exceptions.
            *exc_args: Positional arguments to pass in "exc" instantiation
            *exc_kwargs: Keyword arguments to pass in "exc" instantiation
        """
        self.exc_type = exc_type
        self.exc_args = exc_args
        self.exc_kwargs = exc_kwargs

    def __call__[**P, T](self, f: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(f)
        def _wrap(*args: P.args, **kwargs: P.kwargs) -> T:
            with self:
                return f(*args, **kwargs)

        return _wrap

    def __enter__(self):
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> bool:
        if exc_type is not None and not issubclass(exc_type, self.exc_type):
            raise self.exc_type(
                *self.exc_args, **self.exc_kwargs
            ) from exc_value
        return False


def try_except(
    exc_type: type[BaseException], /, *exc_args, **exc_kwargs
) -> TryExcept:
    """Helper function to instantiate a TryExcept object (aesthetics).

    Args:
        exc_type: Exception to raise in place of the others exceptions.
        *exc_args: Positional arguments to pass in "exc" instantiation
        *exc_kwargs: Keyword arguments to pass in "exc" instantiation
    """
    return TryExcept(exc_type, *exc_args, **exc_kwargs)
