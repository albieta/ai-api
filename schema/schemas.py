from typing import List, TypeVar, Type
import json

T = TypeVar('T', bound='BaseModel')

def individual_serial(item: T) -> dict:
    item['_id'] = str(item['_id'])
    return item

def list_serial(items: List[T]) -> list[dict]:
    return[individual_serial(item) for item in items]