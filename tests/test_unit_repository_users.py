import unittest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar_url

from src.schemas.user import UserSchema


class TestAsyncUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(
            id=1,
            username="Terminator",
            email="terminator@email.com",
            avatar="avatar_path",
            refresh_token="16-bit_code",
            role="admin",
            confirmed=True
        )

    async def test_get_user_by_email(self):
        print("Get user by email...")
        user = self.user
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user

        result = await get_user_by_email(user.email, self.session)

        self.assertEqual(result.username, "Terminator")
        self.assertEqual(result.email, "terminator@email.com")

    async def test_create_user(self):
        print("Create user...")
        body = UserSchema(username="Terminator", email="terminator@email.com", password='qwerty')
        result = await create_user(body, self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        print("Update token...")
        token = '128-bit_key'
        result = await update_token(self.user, token, self.session)
        self.assertIsNone(result)

    async def test_confirmed_email(self):
        print("Confirmed email...")
        user = self.user
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        result = await confirmed_email(user.email, self.session)
        self.assertIsNone(result)

    async def test_update_avatar_url(self):
        print("Update avatar url")
        user = self.user
        mocked_user = MagicMock()
        mocked_user.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mocked_user
        avatar_url = "new_avatar"
        result = await update_avatar_url(user.email, avatar_url, self.session)
        self.assertEqual(result.avatar, avatar_url)


if __name__ == '__main__':
    unittest.main()
