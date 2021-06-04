from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes import auth_router, item_router
from src.util.logging import get_logger
from src.database.database import connect_to_db, close_db_connection

logger = get_logger(__name__)

def get_application():
    app = FastAPI(title=settings.project_name, 
                  version=settings.project_version)  
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router.router)
    app.include_router(item_router.router)
    
    @app.on_event("startup")
    async def startup():
        await connect_to_db(app)
    
    @app.on_event("shutdown")
    async def shutdown():
        await close_db_connection(app)
    
    return app

app = get_application()

@app.get("/")
async def read_root():
    return {"message": f"Welcome to the {settings.project_name} REST API."}
