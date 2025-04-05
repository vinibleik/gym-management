from starlette.config import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL")
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
