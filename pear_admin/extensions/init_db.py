from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # 数据库操作
migrate = Migrate()  # 数据库迁移
