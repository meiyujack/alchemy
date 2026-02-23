from datetime import date
import uuid
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy import select, func
from litestar.plugins.sqlalchemy import SQLAlchemyPlugin, SQLAlchemyAsyncConfig,SQLAlchemyInitPlugin
from litestar.static_files import create_static_files_router

from .models import on_startup,sqlalchemy_config,provide_limit_offset_pagination
from .controller.AuthorController import AuthorController
from .controller.BookController import BookController

static_files_router = create_static_files_router(path="/", directories=["static"])

# async def on_startup(app:Litestar)->None:
#     async with sqlalchemy_config.get_session() as session:
#         statement=select(func.count()).select_from(Author)
#         count=await session.execute(statement)
#         if not count.scalar():
#             author_id=uuid.uuid4()
#             session.add(Author(name="Stephen King",dob=date(1954,9,21),id=author_id))
#             session.add(Book(title="It",author_id=author_id))
#             await session.commit()

app = Litestar(
    route_handlers=[AuthorController,BookController,static_files_router],
    on_startup=[on_startup],
    debug=True,
    plugins=[SQLAlchemyInitPlugin(config=sqlalchemy_config)],
    dependencies={"limit_offset":Provide(provide_limit_offset_pagination)}
)
