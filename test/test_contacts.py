import unittest
from unittest.mock import MagicMock

import datetime

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, '../src')
from src.database.models import Contact,User
from src.schemas import ContactBase,ContactUpdate
from src.repository.contacts import (
    get_contact,
    get_birthdays,
    get_contacts,
    create_contact,
    update_contact,
    delete_contact,
    find_contact
)

class TestNotes(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_contacts(db=self.session,user=self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1
        contact = Contact(id=contact_id,user_id=self.user.id)
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=contact_id, user=self.user, db=self.session)
        self.assertEqual(result, contact)
    
    async def test_create_contact(self):
        contact = ContactBase(
            first_name="Michael",
            last_name="Johnson",
            email="michaelj@example.com",
            phone_num="+380670392310",
            birthday="1997-02-03"
        )

        result = await create_contact(body=contact, user=self.user, db=self.session)

        self.assertEqual(result.first_name, contact.first_name)
        self.assertEqual(result.last_name, contact.last_name)
        self.assertEqual(result.email, contact.email)
        self.assertEqual(result.phone_num, contact.phone_num)
        self.assertEqual(result.birthday, contact.birthday)

    async def test_update_contact(self):
        contact_id = 1
        update_contact_data = ContactUpdate(
            email="example_email@example.com", 
            phone_num="+38067014182"
        )
        contact = Contact(id=contact_id,user_id=self.user.id)

        self.session.query().filter().first.return_value = contact

        result = await update_contact(contact_id=contact_id, body=update_contact_data, user=self.user, db=self.session)

        self.assertEqual(result.email, update_contact_data.email)
        self.assertEqual(result.phone_num, update_contact_data.phone_num)

    async def test_delete_contact(self):
        contact_id = 1
        contact = Contact(id=contact_id, user_id=self.user.id)

        self.session.query().filter().first.return_value = contact

        result = await delete_contact(contact_id=contact_id, user=self.user, db=self.session)

        self.assertEqual(result, contact)

    # async def test_get_birthdays(self):
    #     ...
    
    # async def test_find_contact(self):
    #     ...

if __name__ == '__main__':
    unittest.main()


