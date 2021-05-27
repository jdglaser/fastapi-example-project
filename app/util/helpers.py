from typing import Any, Type, Callable
from app.services.base_service import BaseService

def get_service(service_type: Type[BaseService]) -> Callable:
    def get_service() -> BaseService:
        return service_type()
    return get_service

def remove_from_dict(dictionary: dict[Any, Any], item_to_remove: str) -> dict[Any, Any]:
    return {i:dictionary[i] for i in dictionary if i!=item_to_remove}
