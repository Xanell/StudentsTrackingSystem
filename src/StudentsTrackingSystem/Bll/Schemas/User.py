from datetime import datetime
from pydantic import Field
from Bll.Schemas.Base import BaseSchema
from Bll.Schemas.SchoolClasses import SchoolClassShort
from Core.Enums import RoleName

class UserShort(BaseSchema):
    id: int
    username: str
    last_name: str
    first_name: str
    middle_name: str

class UserDetail(BaseSchema):
    id: int
    username: str
    last_name: str
    first_name: str
    middle_name: str
    role: RoleName
    school_class: SchoolClassShort | None
    deactivated_at: datetime | None  # None активен

class UserCreate(BaseSchema):
    last_name: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str = Field(min_length=1, max_length=50)
    role: RoleName

class UserUpdate(BaseSchema):
    last_name: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=50)
    middle_name: str = Field(min_length=1, max_length=50)
    role: RoleName

class UserCredentials(BaseSchema):
    id: int
    username: str
    password: str

class UserLogin(BaseSchema):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)
