from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os
from authlib.integrations.starlette_client import OAuth

load_dotenv()

DATABASE_URL = os.getenv("NEON_DB")

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()



oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/"
        ".well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    },)