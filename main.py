from sqlmodel import SQLModel
from config.database import engine, get_session
from fastapi import FastAPI, Request
from todos.router import router as todorouter
from fastapi.middleware.cors import CORSMiddleware
from user.router import router as user_router
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from user.limiter import limiter
from starlette.middleware.sessions import SessionMiddleware
from auth.auth import SECRET

app = FastAPI(title="TODO APP")


@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)


app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(router=user_router)
app.include_router(router=todorouter)
