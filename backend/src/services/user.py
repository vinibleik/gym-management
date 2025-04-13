from typing import Any

from src.models.user import UserCreate, UserInDB, UserUpdate
from src.repositories.user import UserRepository
from src.utils.try_except import try_except


class UserServiceError(Exception): ...


class UserServiceValidationError(UserServiceError):
    validation_error: BaseException | None

    def __init__(
        self,
        validation_error: BaseException | None = None,
    ) -> None:
        self.validation_error = validation_error


class UserService:
    repo: UserRepository

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    @try_except(UserServiceError, "Error creating new user")
    def create_user(self, body: Any) -> UserInDB:
        try:
            user = UserCreate(
                **{field: body[field] for field in UserCreate.model_fields()}
            )
        except Exception as e:
            raise UserServiceValidationError(e) from e
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
                    **{
                        field: body[field]
                        for field in UserUpdate.model_fields()
                    }
                )
            except Exception as e:
                raise UserServiceValidationError(e) from e
            else:
                return self.repo.update(user_id, user)

    def delete_user_by_id(self, user_id: int) -> UserInDB | None:
        with try_except(
            UserServiceError, f"Error finding user with id: {user_id}"
        ):
            return self.repo.delete(user_id)
