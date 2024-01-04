import unittest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.repository.contacts import get_contacts, get_all_contacts, get_contact, create_contact, update_contact, \
    delete_contact, search_contacts, search_by_birthday

from src.schemas.contact import ContactSchema


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        print("Get contacts...")
        limit = 10
        offset = 0
        contacts = [Contact(id=1, firstname="firstname1"),
                    Contact(id=2, firstname="firstname2")]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_all_contacts(self):
        print("Get all contacts...")
        limit = 10
        offset = 0
        contacts = [Contact(id=1, firstname="firstname1"),
                    Contact(id=2, firstname="firstname2")]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        print("Get contact...")
        contact = Contact(
            id=1,
            firstname="test",
            lastname="last",
            email="test@email.com",
            phone="0671111111",
            birthday="2024-01-02",
            additional_data="test"
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(1, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        print("Create contact...")
        body = ContactSchema(
            firstname="test",
            lastname="last",
            email="test@email.com",
            phone="0671111111",
            birthday="2024-01-02",
            additional_data="test"
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)

    async def test_update_contact(self):
        print("Update contact...")
        body = ContactSchema(
            firstname=" Dieter",
            lastname="Dierks",
            email="test@email.com",
            phone="0671111111",
            birthday="2024-01-02",
            additional_data="test"
        )
        mocked_todo = MagicMock()
        mocked_todo.scalar_one_or_none.return_value = Contact(
            id=1,
            firstname="test",
            lastname="last",
            email="test@email.com",
            phone="0671111111",
            birthday="2024-01-02",
            additional_data="test"
        )
        self.session.execute.return_value = mocked_todo
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.firstname, body.firstname)
        self.assertEqual(result.lastname, body.lastname)
        self.assertEqual(result.email, body.email)

    async def test_delete_contact(self):
        print("Delete contact...")
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            firstname=" Dieter",
            lastname="Dierks",
            email="test@email.com",
            phone="0671111111",
            birthday="2024-01-02",
            additional_data="test")
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)

    async def test_search_contacts(self):
        print("Search contact...")
        contacts = [Contact(firstname='Martin', lastname='Bird', email='martin@example.com'),
                    Contact(firstname='Mikkey', lastname='Dee', email='dee@example.com')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_contacts('Martin', self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_search_by_birthday(self):
        print("Search contact by birthday...")
        contacts = [Contact(firstname='Martin', lastname='Bird', email='martin@example.com', birthday=date.today()),
                    Contact(firstname='Mikkey', lastname='Dee', email='dee@example.com')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await search_by_birthday(self.session, self.user)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
