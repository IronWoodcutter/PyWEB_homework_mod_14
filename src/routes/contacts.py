from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/contacts', tags=['contacts'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=list[ContactResponse], dependencies=[Depends(RateLimiter(times=1, seconds=5))],
            status_code=status.HTTP_200_OK, )
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of contacts returned
    :param offset: int: Specify the offset of the first contact to return
    :param ge: Specify the minimum value of a parameter, and le is used to specify the maximum value
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user
    :return: A list of contacts, which is a list of dictionaries
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/all", response_model=list[ContactResponse], dependencies=[Depends(access_to_route_all)],
            status_code=status.HTTP_200_OK)
async def get_all_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                           db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The get_all_contacts function returns a list of contacts.
        The limit and offset parameters are optional, with default values of 10 and 0 respectively.
        The limit parameter is used to specify the maximum number of contacts returned in the response body, while the offset parameter is used to specify how many records should be skipped before returning results.

    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the maximum number of contacts that can be returned by a single request
    :param offset: int: Specify the offset of the query
    :param ge: Specify a minimum value for the parameter
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_all_contacts(limit, offset, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))],
            status_code=status.HTTP_200_OK)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is a GET request that returns the contact with the given ID.
    If no such contact exists, it will return a 404 NOT FOUND error.

    :param contact_id: int: Get the contact id from the path
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post("/", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))],
             status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the user from the auth_service
    :return: The created contact
    :doc-author: Trelent
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=2, seconds=5))],
            status_code=status.HTTP_200_OK)
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        It takes an id, body and db as parameters. The id is used to find the contact in the database,
        while body contains all of the information that will be updated for that specific contact.
        The db parameter is used to connect with our PostgreSQL database.

    :param body: ContactSchema: Validate the body of the request
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete("/{contact_id}", dependencies=[Depends(RateLimiter(times=2, seconds=5))],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Get the contact id from the path
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get("/search/", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=2, seconds=5))],
            status_code=status.HTTP_200_OK)
async def search_contacts(query: str = Query(None), db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    """
    The search_contacts function searches for contacts in the database.
        It takes a query string as an argument and returns a list of ContactResponse objects.

    :param query: str: Specify the search query
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the database
    :return: A list of contactresponse objects
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.search_contacts(query, db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return [ContactResponse(**contact.__dict__) for contact in contacts]


@router.get('/birthday_date/', dependencies=[Depends(RateLimiter(times=2, seconds=5))],
            response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def search_by_birthday(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    The search_by_birthday function searches for contacts by birthday.
        Args:
            db (AsyncSession): The database session to use.
            user (User): The current user, as determined by the auth_service dependency.

    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the database
    :return: A list of contacts, where the birthday is today
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.search_by_birthday(db, user)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return [ContactResponse(**contact.__dict__) for contact in contacts]
