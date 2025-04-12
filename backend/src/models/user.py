from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any, ClassVar, Literal

from src.utils.dataclass import (
    FieldError,
    SerializeDataclass,
    validate_dataclass,
)

UserRole = Literal["staff", "personal", "student"]


@validate_dataclass
@dataclass
class UserBase(SerializeDataclass):
    """User shared properties."""

    username: str
    name: str
    date_of_birth: date
    role: UserRole

    USERNAME_MIN_LENGTH: ClassVar[int] = 4
    NAME_MIN_LENGTH: ClassVar[int] = 4
    VALID_ROLES: ClassVar[set[UserRole]] = {"staff", "personal", "student"}

    def __validate_username__(self, name: str, value: Any) -> bool:
        if not isinstance(value, str) or len(value) < self.USERNAME_MIN_LENGTH:
            raise FieldError(
                name,
                value,
                f"username must be a string with at least {self.USERNAME_MIN_LENGTH} characters.",  # noqa
            )

        return True

    def __validate_name__(self, name: str, value: Any) -> bool:
        if not isinstance(value, str) or len(value) < self.NAME_MIN_LENGTH:
            raise FieldError(
                name,
                value,
                f"name must be a string with at least {self.NAME_MIN_LENGTH} characters.",  # noqa
            )
        return True

    def __validate_date_of_birth__(self, name: str, value: Any) -> bool:
        if isinstance(value, datetime):
            self.date_of_birth = value.date()
            return True

        if isinstance(value, date):
            self.date_of_birth = value
            return True

        if isinstance(value, int | float | str):
            try:
                if isinstance(value, str):
                    value = datetime.fromisoformat(value).date()
                else:
                    value = datetime.fromtimestamp(value, tz=UTC).date()
                self.date_of_birth = value
                return True
            except Exception as e:
                raise FieldError(
                    name,
                    value,
                    f"Could not convert {value} to a valid date",
                ) from e

        return False

    def __validate_role__(self, name: str, value: Any) -> bool:
        if isinstance(value, str) and (v := value.lower()) in self.VALID_ROLES:
            self.role = v
            return True
        raise FieldError(
            name,
            value,
            f"User role must be one of the: {', '.join(self.VALID_ROLES)}",
        )

    @property
    def age(self) -> int:
        today = date.today()  # noqa
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )  # Subtract the current year if the day of born was not reached
        )


@validate_dataclass
@dataclass
class UserCreate(UserBase):
    """Properties to receive on User creation."""

    password_hash: str


@validate_dataclass
@dataclass
class UserUpdate(UserBase):
    """Properties to receive on User update."""


@validate_dataclass
@dataclass
class UserInDBBase(UserBase):
    """Properties shared by models stored in Database"""

    id: int


@validate_dataclass
@dataclass
class User(UserInDBBase):
    """Properties to return to the client"""


@validate_dataclass
@dataclass
class UserInDB(UserInDBBase):
    """All User properties stored in Database"""

    password_hash: str
