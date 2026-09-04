import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()
USER = os.environ.get("POSTGRES_USER")
PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB = os.environ.get("POSTGRES_DB")
PORT = os.environ.get("POSTGRES_PORT")
DB_URL = f"postgresql://{USER}:{PASSWORD}@localhost:{PORT}/{DB}"

engine = create_engine(DB_URL, echo=True)

class Base(DeclarativeBase):
	pass