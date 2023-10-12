from fastapi import APIRouter, HTTPException
from typing import List, TypeVar, Type
from pymongo.collection import ReturnDocument
from config.database import db
from schema.schemas import list_serial, individual_serial
from bson import ObjectId

T = TypeVar('T', bound='BaseModel')

class CRUDRoutes:

    def __init__(self, model_type: Type[T], collection_name: str = 'default_collection'):
        self.dynamic_router = APIRouter(tags=[model_type.__name__])
        self.model_type = model_type
        self.collection_name = collection_name

        self.post_item.__annotations__['item'] = model_type
        self.put_item.__annotations__['item'] = model_type

        # GET Request Method
        self.dynamic_router.add_api_route(
            f'/{model_type.__name__.lower()}/', self.get_items, methods=["GET"], response_model=List[dict]
        )

        # POST Request Method
        self.dynamic_router.add_api_route(
            f'/{model_type.__name__.lower()}/', self.post_item, methods=["POST"], response_model=dict
        )

        # PUT Request Method
        self.dynamic_router.add_api_route(
            f'/{model_type.__name__.lower()}/{{item_id}}/', self.put_item, methods=["PUT"], response_model=dict
        )

        # DELETE Request Method
        self.dynamic_router.add_api_route(
            f'/{model_type.__name__.lower()}/{{item_id}}/', self.delete_item, methods=["DELETE"], response_model=dict
        )

    def get_collection(self):
        return db[self.collection_name]

    async def get_items(self, skip: int = 0, limit: int = 10):
        collection = self.get_collection()
        items = collection.find(skip=skip, limit=limit)
        return list_serial(items)

    async def post_item(self, item: T):
        collection = self.get_collection()
        created_result = collection.insert_one(dict(item))
        created_item = collection.find_one({'_id': created_result.inserted_id})
        return individual_serial(created_item)

    async def put_item(self, item_id: str, item: T):
        collection = self.get_collection()
        updated_item = collection.find_one_and_update({'_id': ObjectId(item_id)},{'$set': item.dict()}, return_document=ReturnDocument.AFTER,)
        if updated_item:
            return individual_serial(updated_item)
        raise HTTPException(status_code=404, detail="Item not found")

    async def delete_item(self, item_id: str):
        collection = self.get_collection()
        deleted_item = collection.find_one_and_delete({'_id': ObjectId(item_id)})
        if deleted_item:
            return individual_serial(deleted_item)
        raise HTTPException(status_code=404, detail="Item not found")
