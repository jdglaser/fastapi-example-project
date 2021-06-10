from humps import camelize
from pydantic import BaseModel


class MainModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
