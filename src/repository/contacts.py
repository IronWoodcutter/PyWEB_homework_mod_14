from datetime import date, timedelta

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Specify the number of contacts to return
    :param offset: int: Specify the offset of the query
    :param db: AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_all_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_all_contacts function returns a list of all contacts in the database.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first offset number of rows
    :param db: AsyncSession: Pass in the database session to be used
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the contact id to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Check if the user is allowed to access this contact
    :return: A single contact
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the data passed in by the user
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user_id from the token
    :return: A contact instance
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True),
                      user=user)  # (title=body.title, description=body.description)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Identify the contact to be updated
    :param body: ContactSchema: Get the contact information from the request body
    :param db: AsyncSession: Pass in the database session to the function
    :param user: User: Ensure that the user is only updating their own contacts
    :return: The updated contact
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.firstname = body.firstname
        contact.lastname = body.lastname
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact to delete
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the user from the database
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(query: str, db: AsyncSession, user: User):
    """
    The search_contacts function searches the database for contacts that match a given query.
        The function takes in two arguments:
            - query: A string containing the search term(s) to be used when searching for contacts.
            - db: An asyncpg session object, which is used to execute SQL queries against the database.
        The function returns a list of Contact objects that match the search criteria.

    :param query: str: Search for contacts in the database
    :param db: AsyncSession: Pass in the database session
    :param user: User: Get the user's id
    :return: A list of contacts that match the query
    :doc-author: Trelent
    """
    stmt = select(Contact).where(
        or_(Contact.firstname.ilike(f"%{query}%"),
            Contact.lastname.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%")))
    result = (await db.execute(stmt)).scalars().all()
    return result


async def search_by_birthday(db: AsyncSession, user: User):
    """
    The search_by_birthday function searches the database for contacts whose birthday is within a week of today.
        It returns a list of Contact objects that match these criteria.

    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Pass the user object to the function
    :return: A list of contacts who have a birthday in the next week
    :doc-author: Trelent
    """
    today = date.today()
    end_day = today + timedelta(days=7)

    stmt = select(Contact).where(
        and_(
            Contact.birthday >= today,
            Contact.birthday <= end_day
        )
    )
    result = (await db.execute(stmt)).scalars().all()
    return result
