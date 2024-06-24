from flask import Blueprint, Flask

from .function import function_api
from .department import department_api
from .passport import passport_api
from .rights import rights_api
from .role import role_api
from .user import user_api


def register_apis(app: Flask):
    apis = Blueprint("api", __name__, url_prefix="/api/v1")

    # 登录蓝图
    apis.register_blueprint(passport_api)
    # 权限蓝图
    apis.register_blueprint(rights_api)
    # 角色蓝图
    apis.register_blueprint(role_api)
    # 部门蓝图
    apis.register_blueprint(department_api)
    # 用户蓝图
    apis.register_blueprint(user_api)
    # 自定义蓝图
    apis.register_blueprint(function_api)

    app.register_blueprint(apis)
