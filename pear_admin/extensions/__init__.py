from flask import Flask

from .init_db import db, migrate
from .init_jwt import jwt
from .init_script import register_script
from .init_error_views import init_error_views
from .init_scheduler import scheduler


def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    init_error_views(app)

    register_script(app)
    # 初始化 scheduler
    scheduler.init_app(app)
    scheduler.start()
