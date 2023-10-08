from fastapi import FastAPI, APIRouter
from importlib import import_module
from importlib.machinery import SourceFileLoader
import os
import glob

app = FastAPI()

routes_directory = "routes"

module_names = []

for file_path in glob.glob(os.path.join(routes_directory, "*.py")):
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    module = SourceFileLoader(str(module_name), routes_directory + '/' + str(module_name) + '.py').load_module()
    attribute_value = getattr(module, 'dynamic_router')
    app.include_router(attribute_value)

