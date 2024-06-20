from .ponding import ponding_api
from .summary import summary_api 
from .task import task_api
from flask import Blueprint

function_api = Blueprint("function", __name__, url_prefix='/function')

function_api.register_blueprint(ponding_api)
function_api.register_blueprint(summary_api)
function_api.register_blueprint(task_api)