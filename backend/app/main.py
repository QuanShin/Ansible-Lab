from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Training REST API",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_database() -> Generator[Session, None, None]:
    database = SessionLocal()

    try:
        yield database
    finally:
        database.close()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "training-backend",
        "status": "running",
        "deployed_by": "ansible",
        "version": "2.0.0",
    }


@app.get("/health")
def health(
    database: Session = Depends(get_database),
) -> dict[str, str]:
    try:
        database.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from error


@app.get(
    "/messages",
    response_model=list[schemas.MessageResponse],
)
def list_messages(
    database: Session = Depends(get_database),
) -> list[models.Message]:
    statement = select(models.Message).order_by(
        models.Message.id,
    )

    return list(database.scalars(statement).all())


@app.post(
    "/messages",
    response_model=schemas.MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    payload: schemas.MessageCreate,
    database: Session = Depends(get_database),
) -> models.Message:
    message = models.Message(
        content=payload.content,
    )

    database.add(message)
    database.commit()
    database.refresh(message)

    return message
