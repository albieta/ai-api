from fastapi import APIRouter, HTTPException
from typing import  Dict, Any
from config.database import db
import os, json, subprocess
from importlib.machinery import SourceFileLoader
from pydantic import BaseModel

dynamic_router = APIRouter(tags=["Main"])

def get_collection(collection_name: str = 'default_collection'):
    return db[collection_name]

# CREATE collection
@dynamic_router.post('/create_collection/{collection_name}/', response_model=dict)
async def create_collection(collection_name: str, schema: dict):
    try:
        generated_models = create_model_from_schema(schema, collection_name)
        for model in generated_models:
            create_rest_from_model(model, collection_name)

        return {"message": f"Collection {collection_name} created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collection: {str(e)}")


def create_model_from_schema(schema: Dict[str, Any], collection_name: str):
    models_folder = "models"
    os.makedirs(models_folder, exist_ok=True)

    input_file = f"data/{collection_name}.json"
    with open(input_file, "w") as file:
        json.dump(schema, file)

    output_file = f"{models_folder}/{collection_name}_model.py"

    command = [
        "datamodel-codegen",
        "--input", input_file,
        "--output", output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Model generated successfully and saved to {output_file}")

        module = SourceFileLoader(collection_name, output_file).load_module()

        model_classes = [cls for cls in module.__dict__.values() if isinstance(cls, type) and issubclass(cls, BaseModel) and cls != BaseModel]

        return model_classes
    except subprocess.CalledProcessError as e:
        print(f"Error generating model: {e}")
        return None
    
def create_rest_from_model(model: BaseModel, collection_name: str):
    models_folder = "routes"
    os.makedirs(models_folder, exist_ok=True)

    model_name = model.__name__
    model_name_lower = model_name.lower()
    item_id = '{item_id}'
    

    router_code = f"""from fastapi import APIRouter, HTTPException
from typing import List, TypeVar
from pymongo.collection import ReturnDocument
from config.database import db
from schema.schemas import list_serial, individual_serial
from bson import ObjectId
from models.{collection_name}_model import {model.__name__}

dynamic_router = APIRouter(tags=["{model_name}"])

def get_collection(collection_name: str = 'default_collection'):
    return db[collection_name]

# GET Request Method
@dynamic_router.get('/{model_name_lower}/', response_model=List[dict])
async def get_items(skip: int = 0, limit: int = 10):
    collection = get_collection('{collection_name}')
    items = collection.find(skip=skip, limit=limit)
    return list_serial(items)

# POST Request Method
@dynamic_router.post('/{model_name_lower}/', response_model=dict)
async def create_item(item: {model_name}):
    collection = get_collection('example')
    created_result = collection.insert_one(dict(item))
    created_item = collection.find_one(""" + "{'_id': created_result.inserted_id}" + f""")
    return individual_serial(created_item)

# PUT Request Method
@dynamic_router.put('/{model_name_lower}/{item_id}/', response_model=dict)
async def update_item(item_id: str, item: {model_name}):
    collection = get_collection('{collection_name}')
    updated_item = collection.find_one_and_update(""" + "{'_id': ObjectId(item_id)},{'$set': item.dict()}, return_document=ReturnDocument.AFTER,)" + f"""
    if updated_item:
        return individual_serial(updated_item)
    raise HTTPException(status_code=404, detail="Item not found")

# DELETE Request Method
@dynamic_router.delete('/{model_name_lower}/{item_id}/', response_model=dict)
async def delete_item(item_id: str):
    collection = get_collection('{collection_name}')
    deleted_item = collection.find_one_and_delete(""" + "{'_id': ObjectId(item_id)})" + """
    if deleted_item:
        return individual_serial(deleted_item)
    raise HTTPException(status_code=404, detail="Item not found")

"""
    file_path = os.path.join(models_folder, f"{model_name_lower}_router.py")
    with open(file_path, "w") as file:
        file.write(router_code)
