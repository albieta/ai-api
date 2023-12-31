from fastapi import FastAPI
import os
import glob
import importlib
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

tags_metadata = [
    {
        "name": "Main",
        "description": "This router allows to create models from any given JSON Schema format",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routes_directory = "routes"
models_directory = "models"

for file_path in glob.glob(os.path.join(routes_directory, "*.py")):
    routes_name = os.path.splitext(os.path.basename(file_path))[0]
    routes = importlib.import_module(f"{routes_directory}.{routes_name}")
    
    if routes_name == 'route':
        app.include_router(routes.dynamic_router)

    for file_path in glob.glob(os.path.join(models_directory, "*.py")):
        collection_name = os.path.splitext(os.path.basename(file_path))[0]
        model = importlib.import_module(f"{models_directory}.{collection_name}")
        model_classes = [cls for cls in model.__dict__.values() if isinstance(cls, type) and issubclass(cls, BaseModel) and cls != BaseModel]
        
        for model_class in model_classes:
            if model_class.__name__.lower() in routes_name.lower():
                hobbies = getattr(routes, f"{model_class.__name__}Routes")
                new = hobbies()
                app.include_router(new.dynamic_router)
