from pydantic import BaseModel, Field
from datetime import date,datetime

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_num: str
    birthday: date
   
class ContactResponse(ContactBase):
    id: int 

    class Config:
        orm_mode = True

class ContactUpdate(BaseModel):
    email: str
    phone_num: str

class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6,max_length=10)

class UserDB(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True
    
class UserResponse(BaseModel):
    user: UserDB
    detail: str = "User successfully created"

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"