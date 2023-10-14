from models.user_model import User
from routes.general.general_routes import CRUDRoutes

class UserRoutes(CRUDRoutes):

    def __init__(self):
        super().__init__(model_type=User, collection_name='user')
