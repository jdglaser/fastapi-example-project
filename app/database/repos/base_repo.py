from databases import Database
from starlette.requests import Request

class BaseRepo:
    def __init__(self, request: Request) -> None:
        self.db = request.app.state.db