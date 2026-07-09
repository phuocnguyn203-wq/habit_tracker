from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL
DATABASE_URL = f'sqlite+pysqlite:///{DATABASE_URL}'

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    from app.models import models 
    Base.metadata.create_all(engine)