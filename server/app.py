from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import auth, completion, conversation, status
from db import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(lifespan=lifespan)
for module in (status, auth, conversation, completion):
    app.include_router(module.router)
