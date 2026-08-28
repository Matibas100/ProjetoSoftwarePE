from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


# Instancias unicas, inicializadas pela application factory em app/__init__.py.
db = SQLAlchemy()
cors = CORS()
