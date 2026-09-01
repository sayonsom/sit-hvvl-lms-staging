import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if running in local environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('POSTGRES_DSN')

if DATABASE_URL:
    CONNECTION_KWARGS = {"dsn": DATABASE_URL}
elif ENVIRONMENT == 'local':
    # Local PostgreSQL configuration. These defaults must never point to production.
    SERVER = os.getenv('DB_HOST', 'localhost')
    DATABASE = os.getenv('DB_NAME', 'aligndb')
    USERNAME = os.getenv('DB_USER', 'alignuser')
    PASSWORD = os.getenv('DB_PASSWORD', 'local-dev-password-change-me')
    PORT = int(os.getenv('DB_PORT', '5432'))
    CONNECTION_KWARGS = {
        "host": SERVER,
        "database": DATABASE,
        "user": USERNAME,
        "password": PASSWORD,
        "port": PORT,
    }
else:
    required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Missing required production database environment variables: "
            + ", ".join(missing)
        )
    CONNECTION_KWARGS = {
        "host": os.getenv('DB_HOST'),
        "database": os.getenv('DB_NAME'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD'),
        "port": int(os.getenv('DB_PORT', '5432')),
    }

class DBConnection:
    _pool = None  # Class attribute to hold the pool

    @classmethod
    async def init(cls):  # Initialize as a class method
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                **CONNECTION_KWARGS
            )

    async def __aenter__(self):
        if self._pool is None:
            await self.init()  # Make sure the pool is initialized
        self.conn = await self._pool.acquire()
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        await self._pool.release(self.conn)

# Ensure that you have an async generator to use as a dependency in FastAPI
async def get_db_connection():
    db_conn = DBConnection()
    async with db_conn as conn:
        yield conn

