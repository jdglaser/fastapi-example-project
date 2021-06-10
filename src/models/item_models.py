from src.models.main_model import MainModel


class Item(MainModel):
    id: int
    name: str
    description: str
    completed: bool

class ItemTemplate(MainModel):
    name: str
    description: str

class ItemUpdate(MainModel):
    description: str
    completed: bool
