import logging
import sqlite3
from collections.abc import Generator
from contextlib import asynccontextmanager, contextmanager

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route

from src.config import APP_NAME, DATABASE_URL
from src.routes import user_routes

logger = logging.getLogger(APP_NAME)


async def health_check(_):
    return PlainTextResponse("Server is OK")


@contextmanager
def db_connection(url: str) -> Generator[sqlite3.Connection, None, None]:
    conn = None
    try:
        conn = sqlite3.connect(url)
        yield conn
    except Exception:
        logger.exception("Couldn't connect to database on %s", url)
    finally:
        if conn:
            conn.close()


@asynccontextmanager
async def lifespan(app: Starlette):
    with db_connection(DATABASE_URL) as conn:
        app.state.APP_NAME = APP_NAME
        yield {"conn": conn}


routes = [
    Route("/health-check", health_check),
    Mount("/api/v1/users", routes=user_routes),
]

app = Starlette(debug=True, routes=routes, lifespan=lifespan)
