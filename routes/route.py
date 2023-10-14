from fastapi import APIRouter, HTTPException
from routes.general.auto_generate_routes import create_model_from_schema, create_rest_from_model
from typing import List
import os
import json

dynamic_router = APIRouter(tags=["Main"])

# CREATE collections
@dynamic_router.post('/create_collection/{collection_name}/', response_model=dict)
async def create_collection(collection_name: str, schema: dict):
    try:
        generated_models = create_model_from_schema(schema, collection_name)
        for model in generated_models:
            create_rest_from_model(model, collection_name)

        return {"message": f"Collection {collection_name} created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating collection: {str(e)}")

# GET all models
@dynamic_router.get('/models', response_model=List[dict])
async def get_models():
    try:
        schema_files = [file for file in os.listdir("./data") if file.endswith('.json')]

        schemas = []
        for schema_file in schema_files:
            schema_path = os.path.join("./data", schema_file)
            with open(schema_path, 'r') as file:
                schema_content = json.load(file)
                schemas.append(schema_content)

        return schemas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")
