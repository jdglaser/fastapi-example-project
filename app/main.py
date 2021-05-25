from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from app.config import settings
from app.database.database import db
from app.routes import auth_router, item_router
from app.util.logging import get_logger

app = FastAPI()

logger = get_logger(__name__)

app.include_router(item_router.router)
app.include_router(auth_router.router)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get("/")
async def read_root():
    logger.info("HELLO!")
    return {"message": f"Welcome to the {settings.project_name} REST API."}
