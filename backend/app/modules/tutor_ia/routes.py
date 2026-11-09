from flask import Blueprint
from app.modules.tutor_ia.controllers.tutoria_controller import TutoriaController

blueprint = Blueprint('tutor_ia', __name__)
blueprint.add_url_rule('/tutoria', view_func=TutoriaController.gerar, methods=['POST'])
