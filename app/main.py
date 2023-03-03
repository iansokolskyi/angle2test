import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.admin import admin
from app.core.db import create_db_and_tables
from app.core.storage import MEDIA_ROOT
from app.routers import users, articles

app = FastAPI(
    title="Test Task API",
    description="Angle2 Test Task API",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/docs/redoc",
)
# app.add_middleware(SessionMiddleware, , max_age=None)

# routes
app.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
app.include_router(
    articles.router,
    prefix="/articles",
    tags=["articles"],
    responses={404: {"description": "Not found"}},
)

# static files
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
app.mount("/storage", StaticFiles(directory=MEDIA_ROOT), name="storage")
admin.mount_to(app)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
