from uuid import UUID

from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.repository import filters
from litestar.pagination import OffsetPagination
from litestar.params import Parameter
# from pydantic import TypeAdapter
from litestar.dto import DTOData

from alchemy.models import provide_authors_repo,provide_author_details_repo, AuthorRepository, Author
from alchemy.schemas import AuthorCreate,AuthorRead,AuthorUpdate,BookRead


class AuthorController(Controller):
    """Author CRUD"""

    dependencies = {"authors_repo": Provide(provide_authors_repo)}

    @get(path="/authors",dependencies={"authors_repo": Provide(provide_author_details_repo)})
    async def list_authors(
        self, authors_repo: AuthorRepository, limit_offset: filters.LimitOffset
    ) -> OffsetPagination[AuthorRead]:
        """List authors."""
        results, total = await authors_repo.list_and_count(limit_offset)
        # type_adapter = TypeAdapter(list[AuthorRead])
        authors=[
            AuthorRead(id=author.id,name=author.name,dob=author.dob,books=[BookRead(id=book.id,title=book.title) for book in author.books if author.books]) for author in results
        ]
        return OffsetPagination[AuthorRead](
            items=[authors],#type_adapter.validate_python(results),
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )
    
    @post(path="/authors")
    async def create_author(self,authors_repo: AuthorRepository, data:AuthorCreate)->AuthorRead:
        """Create an author."""
        obj=await authors_repo.add(Author(name=data.name,dob=data.dob))#**data.model_dump(exclude_unset=True,exclude_none=True)))
        await authors_repo.session.commit()
        return AuthorRead(id=obj.id,name=obj.name,dob=obj.dob,books=[BookRead(id=book.id,title=book.title) for book in obj.books if obj.books])#AuthorRead.model_validate(obj)

    @get(path="/authors/{author_id:uuid}",dependencies={"authors_repo": Provide(provide_author_details_repo)})
    async def get_author(self,authors_repo: AuthorRepository, author_id:UUID=Parameter(title="Author ID",description="The author to retrieve."))->AuthorRead:
        """Get an existing author."""
        obj=await authors_repo.get(author_id)
        return AuthorRead(id=obj.id,name=obj.name,dob=obj.dob,books=[BookRead(id=book.id,title=book.title) for book in obj.books if obj.books])#AuthorRead.model_validate(obj)

    @patch(path="/authors/{author_id:uuid}",dependencies={"authors_repo": Provide(provide_author_details_repo)})
    async def update_author(self,authors_repo:AuthorRepository,data:AuthorUpdate,author_id:UUID=Parameter(title="Author ID",description="The author to update."))->Author:
        """Update an author."""
        # raw_obj=data.model_dump(exclude_unset=True,exclude_none=True)
        # raw_obj.update({"id":author_id})
        # obj=await authors_repo.update(Author(**raw_obj))
        # await authors_repo.session.commit()
        raw=data.__dict__
        raw.update({"id":author_id})
        obj=await authors_repo.update(Author(**raw))
        await authors_repo.session.commit()
        return AuthorRead(id=obj.id,name=obj.name,dob=obj.dob,books=[BookRead(id=book.id,title=book.title) for book in obj.books if obj.books]) #AuthorRead.model_validate(obj)
    
    @delete(path="/authors/{author_id:uuid}")
    async def delete_author(self,authors_repo:AuthorRepository,author_id:UUID=Parameter(title="Author ID",description="The author to delete."))->None:
        """Delete a author from the system."""
        _=await authors_repo.delete(author_id)
        await authors_repo.session.commit()
        return AuthorRead(id=_.id,name=_.name,dob=_.dob,books=[BookRead(id=book.id,title=book.title) for book in _.books if _.books])