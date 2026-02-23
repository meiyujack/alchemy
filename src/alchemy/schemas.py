from datetime import date
from uuid import UUID

from pydantic import BaseModel as _BaseModel

class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""
    model_config={"from_attributes":True}

class AuthorRead(BaseModel):
    id:UUID|None
    name:str
    dob:date|None=None
    books:list[BookRead]

class AuthorCreate(BaseModel):
    name:str
    dob:date|None=None

class AuthorUpdate(BaseModel):
    name:str|None=None
    dob:date|None=None

class BookRead(BaseModel):
    id:UUID|None
    title:str

class BookCreate(BaseModel):
    title:str
    author_id:UUID

class BookUpdate(BaseModel):
    title:str