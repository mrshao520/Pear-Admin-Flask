import os
from datetime import timedelta
from flask_apscheduler.auth import HTTPBasicAuth
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "pear-admin-flask")

    SQLALCHEMY_DATABASE_URI = ""

    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # 设置时区，时区不一致会导致定时任务的时间错误
    # SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    # 一定要开启API功能，这样才可以用api的方式去查看和修改定时任务
    SCHEDULER_API_ENABLED = True
    # api前缀（默认是/scheduler）
    SCHEDULER_API_PREFIX = "/scheduler"
    # 配置允许执行定时任务的主机名
    SCHEDULER_ALLOWED_HOSTS = ["*"]
    # auth验证。默认是关闭的，
    # SCHEDULER_AUTH = HTTPBasicAuth()
    # 设置定时任务的执行器（默认是最大执行数量为30的线程池）
    SCHEDULER_EXECUTORS = {"default": {"type": "threadpool", "max_workers": 30}}

    OPEN_PONDING_SERVER = True
    PONDING_EXTRACT = "http://127.0.0.1:8886/extract"
    UNTREATED_FILENAME = "./instance/untreated.txt"
    CSV_FILENAME = "./instance/data.csv"
    CSV_HEADERS = [
        "id",
        "date",
        "time",
        "city",
        "position",
        "longitude",
        "latitude",
        "depth_value",
        "description",
    ]


class DevelopmentConfig(BaseConfig):
    """开发配置"""

    SQLALCHEMY_DATABASE_URI = "sqlite:///pear_admin.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 存储定时任务
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(
            url="sqlite:///instance/pear_admin.db", tablename="ums_task_scheduler"
        )
    }


class TestingConfig(BaseConfig):
    """测试配置"""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # 内存数据库


class ProductionConfig(BaseConfig):
    """生成环境配置"""

    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/pear_admin"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {"dev": DevelopmentConfig, "test": TestingConfig, "prod": ProductionConfig}
