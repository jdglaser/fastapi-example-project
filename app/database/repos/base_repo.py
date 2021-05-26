from databases import Database

class BaseRepo:
    def __init__(self, db: Database) -> None:
        self.db = db