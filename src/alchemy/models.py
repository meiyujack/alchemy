from datetime import date
import datetime
from rich import console
from typing import List
from uuid import UUID
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from litestar.contrib.sqlalchemy import base, repository
from litestar.plugins.sqlalchemy import AsyncSessionConfig, SQLAlchemyAsyncConfig,SQLAlchemyInitPlugin,base
from litestar.params import Parameter
from litestar.repository import filters
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy import ForeignKey



class Author(base.UUIDBase):
    __tablename__ = "author"
    name: Mapped[str]
    dob: Mapped[date]
    books: Mapped[List[Book]] = relationship(back_populates="author", lazy="noload")


class AuthorRepository(repository.SQLAlchemyAsyncRepository[Author]):
    model_type = Author


class Book(base.UUIDAuditBase):
    __tablename__ = "book"
    title: Mapped[str]
    author_id: Mapped[UUID] = mapped_column(ForeignKey("author.id"))
    author: Mapped[Author] = relationship(lazy="joined", innerjoin=True, viewonly=True)

class BookRepository(repository.SQLAlchemyAsyncRepository[Book]):
    model_type = Book

session_config=AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config=SQLAlchemyAsyncConfig(
    connection_string="sqlite+aiosqlite:///test.sqlite",session_config=session_config
)
sqlalchemy_plugin=SQLAlchemyInitPlugin(config=sqlalchemy_config)

async def on_startup()->None:
    """Initializes the database."""
    async with sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(base.UUIDBase.metadata.create_all)


# engine = create_async_engine("sqlite+aiosqlite:///test.sqlite", future=True)
# session_factory = async_sessionmaker(engine, expire_on_commit=False)


# @asynccontextmanager
# async def repository_factory() -> AsyncIterator[AuthorRepository]:
#     async with session_factory() as db_session:
#         try:
#             yield AuthorRepository(session=db_session)
#         except Exception:
#             await db_session.rollback()
#         else:
#             await db_session.commit()


async def provide_authors_repo(db_session: AsyncSession) -> AuthorRepository:
    return AuthorRepository(session=db_session)

async def provide_author_details_repo(db_session: AsyncSession) -> AuthorRepository:
    """This provides a simple example demonstrating how to override the join options for the repository."""
    return AuthorRepository(statement=select(Author).options(selectinload(Author.books)),session=db_session)

async def provide_books_repo(db_session: AsyncSession) -> BookRepository:
    return BookRepository(session=db_session)

async def provide_limit_offset_pagination(
    current_page:int=Parameter(ge=1,query="currentPage",default=1,required=False),
    page_size:int=Parameter(query="pageSize",ge=1,default=10,required=False)
)->filters.LimitOffset:
    """Add offset/limit pagination.
    Return type consumed by `Repository.apply_limit_offset_pagination()`.
    Parameters
    ----------
    current_page:int
        LIMIT to apply to select.
    page_size:int
        OFFSET to apply to select.
    """
    return filters.LimitOffset(page_size,page_size*(current_page-1))