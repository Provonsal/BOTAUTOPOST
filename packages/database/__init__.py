from contextlib import asynccontextmanager
import logging
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from config import Config
from packages.database.models.base import Base


log_dir = Config.GetValue("LOG_DIR")
log_dir = log_dir if log_dir is not None else ""

db_logger = logging.getLogger("database_module")
db_logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{log_dir}database_module.log", mode='w')
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

db_logger.addHandler(console_handler)
db_logger.addHandler(handler)


db_logger.debug(f"Logger for database module successfully created.")


# Getting environment variables for database connection.
USER_DATABASE = Config.GetValue("DATABASE_USER")
PASS_DATABASE = Config.GetValue("DATABASE_PASS")
HOST_DATABASE = Config.GetValue("DATABASE_HOST")
PORT_DATABASE = Config.GetValue("DATABASE_PORT")
NAME_DATABASE = Config.GetValue("DATABASE_NAME")

if all(
    [USER_DATABASE,
    PASS_DATABASE,
    HOST_DATABASE,
    PORT_DATABASE,
    NAME_DATABASE]
    ):
    db_logger.info("All connection string arguments successfully extracted from environment.")
else:
    exc = False
    
    if not USER_DATABASE or USER_DATABASE is None:
        db_logger.error("Argument USER_DATABASE not extracted from environment.")
    if not PASS_DATABASE or PASS_DATABASE is None:
        db_logger.error("Argument PASS_DATABASE not extracted from environment.")
    if not HOST_DATABASE or HOST_DATABASE is None:
        db_logger.error("Argument HOST_DATABASE not extracted from environment.")
    if not PORT_DATABASE or PORT_DATABASE is None:
        db_logger.error("Argument PORT_DATABASE not extracted from environment.")
    if not NAME_DATABASE or NAME_DATABASE is None:
        db_logger.error("Argument NAME_DATABASE not extracted from environment.")
        
    if exc:
        raise ValueError("One of the arguments are not right. Check database_module.log for details.")

# Creating connecting string.
URL_DATABASE = f"postgresql+asyncpg://{USER_DATABASE}:{PASS_DATABASE}@{HOST_DATABASE}:{PORT_DATABASE}/{NAME_DATABASE}"

db_logger.info("Connection string successfully created without any troubles.")

# Creating engine to work with database.
engine = create_async_engine(URL_DATABASE, echo=False)

db_logger.info("Database engine created.")

# Creating session maker to manage database sessions.
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False
)

db_logger.info("Async session maker created.")

async def init_db():
    """Initialize database models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        db_logger.info("Models are created and initialized.")

@asynccontextmanager
async def get_session():
    """**Async context manager generator** yielding database sessions. On **exceptions** rolling back changes."""
    session = async_session_maker()
    try:
        yield session
        
        db_logger.info("Database session has been used and probably something changed. Trying to commit...")
        
        await session.commit()
        
        db_logger.info("Changes successfully commited into database.")

    except Exception as e:
        await session.rollback()
        db_logger.exception("Something went wrong during sql queries.")
        raise e
    
    finally:
        await session.close()
        db_logger.info("Database session closed.")