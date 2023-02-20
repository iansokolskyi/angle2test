from environs import Env
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

env = Env()
env.read_env()

DB_USER = env("DB_USER")
DB_PASSWORD = env("DB_PASSWORD")
DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT")
DB_NAME = env("DB_NAME")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
Base.metadata.bind = engine
