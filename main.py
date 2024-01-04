import re
from typing import Callable
from pathlib import Path

from pydantic import EmailStr, BaseModel

import redis.asyncio as redis
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.conf.config import config
from src.database.db import get_db
from src.routes import contacts, auth, users

app = FastAPI()
BASE_DIR = Path(__file__).parent
directory = BASE_DIR / "src" / "static"
app.mount("/src/static", StaticFiles(directory=directory), name="static")
app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")

templates = Jinja2Templates(directory=BASE_DIR / "src" / "templates")

origins = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_agent_ban_list = [r"bot-Yandex"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )
    await FastAPILimiter.init(r)


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def read_root(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "title": "Contacts App"}
    )


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
