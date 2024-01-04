from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    firstname: str = Field(min_length=3, max_length=50)
    lastname: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=3, max_length=30)
    birthday: date = Field(format="%Y-%m-%d")
    additional_data: str = Field(min_length=3, max_length=250)


class ContactResponse(BaseModel):
    id: int = 1
    firstname: str
    lastname: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: str
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None
    model_config = ConfigDict(from_atributes = True) # noqa

