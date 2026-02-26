from datetime import date
from uuid import UUID

# from pydantic import BaseModel as _BaseModel
from dataclasses import dataclass

# class BaseModel(_BaseModel):
#     """Extend Pydantic's BaseModel to enable ORM mode"""
#     model_config={"from_attributes":True}
@dataclass
class AuthorBase:
    name:str
    dob:date

@dataclass
class AuthorRead(AuthorBase):
    id:UUID
    books:list[BookRead]

@dataclass
class AuthorCreate(AuthorBase):
    pass

@dataclass
class AuthorUpdate:
    name:str|None=None
    dob:date|None=None

@dataclass
class BookBase:
    title:str

@dataclass
class BookRead(BookBase):
    id:UUID

@dataclass
class BookCreate(BookBase):
    author_id:UUID

@dataclass
class BookUpdate(BookBase):
    pass