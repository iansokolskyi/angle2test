import os

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.db import engine, Base
from app.core.dependencies import get_current_user
from app.core.storage import MEDIA_ROOT
from app.routers import users, articles

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Test Task API",
    description="Angle2 Test Task API",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/docs/redoc",
)

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
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# static files
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
app.mount("/storage", StaticFiles(directory=MEDIA_ROOT), name="storage")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
