from abc import ABC, abstractmethod
from typing import override

from src.models.user import UserCreate, UserInDB, UserUpdate


class UserRepositoryError(Exception):
    """Exception raised by errors on operations in UserRepository"""


class UserRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[UserInDB]:
        """Returns all users in store.

        Raises:
            UserRepositoryError: If the underline operation in user store failed
        """

    @abstractmethod
    def find_by_id(self, user_id: int) -> UserInDB | None:
        """Find a user by Id.

        Args:
            user_id: The id of the user.

        Returns:
            The user with the specified id or None if no such user was found.

        Raises:
            UserRepositoryError: If the underline operation in user store failed
        """

    @abstractmethod
    def create(self, user: UserCreate) -> UserInDB:
        """Create a new user in store.

        Args:
            user: The new user to be created.

        Returns:
            The newly created user record on store.

        Raises:
            UserRepositoryError: If the underline operation in user store failed
        """

    @abstractmethod
    def delete(self, user_id: int) -> UserInDB | None:
        """Delete a user in store.

        Args:
            user_id: The id of the user.

        Returns:
            The deleted user or None if the user was not found.

        Raises:
            UserRepositoryError: If the underline operation in user store failed
        """

    @abstractmethod
    def update(self, user_id: int, user: UserUpdate) -> UserInDB | None:
        """Update a user in store.

        Args:
            user_id: The id of the user to be updated.
            user: The new data to be updated in user.

        Returns:
            The updated user of None if the user was not found.

        Raises:
            UserRepositoryError: If the underline operation in user store failed
        """


class InMemoryUserRepository(UserRepository):
    _data: dict[int, UserInDB]
    _cur_index: int

    def __init__(self) -> None:
        self._data = {}
        self._cur_index = 0

    @override
    def find_all(self) -> list[UserInDB]:
        return list(self._data.values())

    @override
    def find_by_id(self, user_id: int) -> UserInDB | None:
        return self._data.get(user_id, None)

    @override
    def create(self, user: UserCreate) -> UserInDB:
        new_user_id = self._cur_index
        new_user = UserInDB.from_user_create(new_user_id, user)
        self._data[new_user_id] = new_user
        self._cur_index += 1
        return new_user

    @override
    def delete(self, user_id: int) -> UserInDB | None:
        return self._data.pop(user_id, None)

    @override
    def update(self, user_id: int, user: UserUpdate) -> UserInDB | None:
        u = self.find_by_id(user_id)
        if u is None:
            return None
        u = UserInDB(**{**u.to_dict(), **user.to_dict()})
        self._data[u.id] = u
        return u
