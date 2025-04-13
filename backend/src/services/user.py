from dataclasses import asdict, is_dataclass
from typing import Any

from src.models.user import UserCreate, UserInDB, UserUpdate
from src.repositories.user import UserRepository
from src.utils.dataclass import ValidationError
from src.utils.try_except import try_except


class UserServiceError(Exception): ...


class UserServiceValidationError(UserServiceError):
    validation_error: ValidationError | None
    body_err: str | None

    def __init__(
        self,
        *,
        body_err: str | None = None,
        validation_error: ValidationError | None = None,
    ) -> None:
        self.body_err = body_err
        self.validation_error = validation_error


class UserService:
    repo: UserRepository

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def _parse_body(
        self, body: Any, required_keys: list[str]
    ) -> dict[str, Any]:
        if is_dataclass(body) and not isinstance(body, type):
            body = asdict(body)
        if not isinstance(body, dict):
            raise UserServiceValidationError(
                body_err=f"Invalid body type: {type(body)}"
            )
        missing_keys: list[str] = []
        parsed_body: dict[str, Any] = {}
        for key in required_keys:
            try:
                parsed_body[key] = body[key]
            except KeyError:
                missing_keys.append(key)

        if missing_keys:
            raise UserServiceValidationError(
                body_err=f"Invalid Body missing keys: {', '.join(missing_keys)}"
            )
        return parsed_body

    @try_except(UserServiceError, "Error creating new user")
    def create_user(self, body: Any) -> UserInDB:
        try:
            user = UserCreate(
                **self._parse_body(body, UserCreate.model_fields())
            )
        except ValidationError as e:
            raise UserServiceValidationError(validation_error=e) from e
        else:
            return self.repo.create(user)

    @try_except(UserServiceError, "Error finding all users")
    def find_all_users(self) -> list[UserInDB]:
        return self.repo.find_all()

    def find_user_by_id(self, user_id: int) -> UserInDB | None:
        with try_except(
            UserServiceError, f"Error finding user with id: {user_id}"
        ):
            return self.repo.find_by_id(user_id)

    def update_user(self, user_id: int, body: Any) -> UserInDB | None:
        with try_except(UserServiceError, f"Error updating user {user_id}"):
            try:
                user = UserUpdate(
                    **self._parse_body(body, UserUpdate.model_fields())
                )
            except ValidationError as e:
                raise UserServiceValidationError(validation_error=e) from e
            else:
                return self.repo.update(user_id, user)

    def delete_user_by_id(self, user_id: int) -> UserInDB | None:
        with try_except(
            UserServiceError, f"Error finding user with id: {user_id}"
        ):
            return self.repo.delete(user_id)
