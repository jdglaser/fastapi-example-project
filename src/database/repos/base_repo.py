from databases import Database
from starlette.requests import Request
from fastapi import Depends

def get_database(request: Request) -> Database:
    return request.app.state.db
    

class BaseRepo:
    def __init__(self, db: Database = Depends(get_database)) -> None:
        self.db = db