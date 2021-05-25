from typing import Mapping

def remove_from_dict(dictionary: Mapping, item_to_remove: str) -> Mapping:
    return {i:dictionary[i] for i in dictionary if i!=item_to_remove}