import os
from dotenv import load_dotenv

load_dotenv()

jwt_secret = os.getenv('JWT_SECRET')
jwt_algorithm = os.getenv('JWT_ALGORITHM')