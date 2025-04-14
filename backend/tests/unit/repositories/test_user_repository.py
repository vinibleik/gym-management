import unittest
from datetime import date

from src.models.user import UserCreate, UserInDB, UserUpdate
from src.repositories.user import InMemoryUserRepository


class TestInMemoryUserRepository(unittest.TestCase):
    repo: InMemoryUserRepository
    user_create: UserCreate
    user_update1: UserUpdate
    user_update2: UserUpdate
    user_in_db_1: UserInDB
    user_in_db_2: UserInDB
    user_updated_in_db_1: UserInDB
    user_updated_in_db_2: UserInDB

    def setUp(self) -> None:
        self.repo = InMemoryUserRepository()
        self.user_create = UserCreate(
            username="username",
            name="name",
            date_of_birth=date(1999, 9, 9),
            role="staff",
            password_hash="hash",
        )
        self.user_update1 = UserUpdate(
            username="new_username",
            name="new_name",
            date_of_birth=date(1999, 9, 9),
            role="staff",
        )
        self.user_update2 = UserUpdate(
            username="username",
            name="name",
            date_of_birth=date(1999, 9, 9),
            role="staff",
        )
        self.user_in_db_1 = UserInDB(
            id=0,
            username="username",
            name="name",
            date_of_birth=date(1999, 9, 9),
            role="staff",
            password_hash="hash",
        )
        self.user_in_db_2 = UserInDB(
            id=1,
            username="username",
            name="name",
            date_of_birth=date(1999, 9, 9),
            role="staff",
            password_hash="hash",
        )
        self.user_updated_in_db_1 = UserInDB(
            id=0,
            username="new_username",
            name="new_name",
            date_of_birth=date(1999, 9, 9),
            role="staff",
            password_hash="hash",
        )
        self.user_updated_in_db_2 = UserInDB(
            id=1,
            username="username",
            name="name",
            date_of_birth=date(1999, 9, 9),
            role="staff",
            password_hash="hash",
        )

    def test_create(self):
        self.repo.create(self.user_create)
        self.assertEqual(self.repo._cur_index, 1)
        self.assertDictEqual(
            self.repo._data,
            {0: self.user_in_db_1},
        )
        self.repo.create(self.user_create)
        self.assertEqual(self.repo._cur_index, 2)
        self.assertDictEqual(
            self.repo._data,
            {0: self.user_in_db_1, 1: self.user_in_db_2},
        )

    def test_find_all(self):
        self.assertListEqual(self.repo.find_all(), [])
        self.repo.create(self.user_create)
        self.assertListEqual(self.repo.find_all(), [self.user_in_db_1])
        self.repo.create(self.user_create)
        self.assertListEqual(
            self.repo.find_all(), [self.user_in_db_1, self.user_in_db_2]
        )

    def test_find_by_id(self):
        self.assertIsNone(self.repo.find_by_id(999))
        self.repo.create(self.user_create)
        self.repo.create(self.user_create)
        self.assertEqual(self.repo.find_by_id(0), self.user_in_db_1)
        self.assertEqual(self.repo.find_by_id(1), self.user_in_db_2)

    def test_delete(self):
        self.assertIsNone(self.repo.delete(999))
        self.repo.create(self.user_create)
        self.repo.create(self.user_create)
        self.assertEqual(self.repo.delete(0), self.user_in_db_1)
        self.assertDictEqual(
            self.repo._data,
            {1: self.user_in_db_2},
        )
        self.assertEqual(self.repo.delete(1), self.user_in_db_2)
        self.assertDictEqual(self.repo._data, {})

    def test_update(self):
        self.repo.create(self.user_create)
        self.repo.create(self.user_create)
        self.assertIsNone(self.repo.update(999, self.user_update1))
        self.assertEqual(
            self.repo.update(0, self.user_update1), self.user_updated_in_db_1
        )
        self.assertEqual(
            self.repo.update(1, self.user_update2), self.user_updated_in_db_2
        )
