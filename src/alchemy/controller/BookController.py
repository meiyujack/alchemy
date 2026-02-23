from uuid import UUID

from litestar import Controller,get,post,patch,delete
from litestar.di import Provide
from litestar.repository import filters
from litestar.pagination import OffsetPagination
from litestar.params import Parameter
from pydantic import TypeAdapter

from ..schemas import BookRead,BookCreate,BookUpdate

from ..models import provide_books_repo,BookRepository,Book

class BookController(Controller):
    dependencies={"books_repo":Provide(provide_books_repo)}

    @get(path="/books")
    async def list_books(self,books_repo:BookRepository,limit_offset:filters.LimitOffset)->OffsetPagination[BookRead]:
        results,total=await books_repo.list_and_count(limit_offset)
        type_adapter=TypeAdapter(list[BookRead])
        return OffsetPagination[BookRead](
            items=type_adapter.validate_python(results),
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset
        )
    
    @post(path="/books")
    async def create_books(self,books_repo:BookRepository,data:BookCreate)->BookRead:
        obj=await books_repo.add(Book(**data.model_dump(exclude_unset=True,exclude_none=True)))
        await books_repo.session.commit()
        return BookRead.model_validate(obj)
    
    @patch(path="/books/{book_id:uuid}")
    async def update_book(self,books_repo:BookRepository,data:BookUpdate,book_id:UUID=Parameter(title="Book ID",description="The book to update."))->BookRead:
        raw_obj=data.model_dump(exclude_unset=True,exclude_none=True)
        raw_obj.update({"id":book_id})
        obj=await books_repo.update(Book(**raw_obj))
        await books_repo.session.commit()
        return BookRead.model_validate(obj)
    
    @delete(path="/books/{book_id:uuid}")
    async def delete_book(self,books_repo:BookRepository,book_id:UUID=Parameter(title="Book ID",description="The book to delete."))->None:
        _=await books_repo.delete(book_id)
        await books_repo.session.commit()