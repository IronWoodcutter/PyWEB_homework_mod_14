import pickle

import cloudinary
import cloudinary.uploader

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    Query,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import contacts as repositories_contacts
from src.repository import users as repositories_users
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.conf.config import config

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=5))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Get the current user
    :return: The user object, which is stored in the database
    :doc-author: Trelent
    """
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=5))],
)
async def get_current_user(
    file: UploadFile = File(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    The get_current_user function is a dependency that will be used in the
        get_current_user endpoint. It takes an UploadFile object, which is a file
        uploaded by the user, and returns a User object with its avatar URL updated.

    :param file: UploadFile: Get the file from the request
    :param db: AsyncSession: Connect to the database
    :param user: User: Get the current user
    :param : Get the current user
    :return: The current user, based on the token
    :doc-author: Trelent
    """
    public_id = f"Web16/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)

    return user
