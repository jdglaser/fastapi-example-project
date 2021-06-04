from typing import Any, Type, Callable

def remove_from_dict(dictionary: dict[Any, Any], item_to_remove: str) -> dict[Any, Any]:
    return {i:dictionary[i] for i in dictionary if i!=item_to_remove}
