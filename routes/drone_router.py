from models.drone_model import Drone
from routes.general.general_routes import CRUDRoutes

class DroneRoutes(CRUDRoutes):

    def __init__(self):
        super().__init__(model_type=Drone, collection_name='drone')
