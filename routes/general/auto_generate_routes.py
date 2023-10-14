from typing import  Dict, Any
from config.database import db
import os, json, subprocess
from importlib.machinery import SourceFileLoader
from pydantic import BaseModel

def get_collection(collection_name: str = 'default_collection'):
    return db[collection_name]

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
    

    router_code = f"""from models.{collection_name}_model import {model.__name__}
from routes.general.general_routes import CRUDRoutes

class {model.__name__}Routes(CRUDRoutes):

    def __init__(self):
        super().__init__(model_type={model.__name__}, collection_name='{model_name_lower}')
"""
    
    file_path = os.path.join(models_folder, f"{model_name_lower}_router.py")
    with open(file_path, "w") as file:
        file.write(router_code)

