import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.schemas import UserModel
from src.database.models import User
from src.repository.users import (
    get_user_by_email, 
    create_user,
    update_token, 
    confirmed_email, 
    update_avatar
    )

class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email(self):
        email = "test@example.com"
        user = User(email=email)

        self.session.query().filter().first.return_value = user

        result = await get_user_by_email(email, self.session)

        self.assertEqual(result,user)

    async def test_create_user(self):
        body = UserModel(username="user123", email="example@gmail.com", password="123456789")
        user = User(id=1, email=body.email)

        result = await create_user(body=body, db=self.session)

        self.assertEqual(result.email, user.email)

    async def test_update_token(self):
        user = User(id=1,email = 'example@gmail.com')
        token = "update_token"

        await update_token(user,token,self.session)

        self.assertEqual(user.refresh_token, token)

    async def test_confirmed_email(self):
        email = "example@gmail.com"
        user = User(id=1, email=email, confirmed=True)
        
        await confirmed_email(email=email, db=self.session)

        self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        email = "example@gmail.com"
        avatar = "https://www.avatar.com/avatar.jpg"

        updated_user = await update_avatar(email=email, url=avatar, db=self.session)
        self.assertEqual(updated_user.avatar, avatar)






if __name__ == "__main__":
    unittest.main()