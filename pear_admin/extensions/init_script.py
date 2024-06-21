import csv
import os

from flask import Flask, current_app

from pear_admin.extensions import db
from pear_admin.orms import (
    DepartmentORM,
    RightsORM,
    RoleORM,
    UserORM,
    DataPondingORM,
    ChannelsORM,
)
from datetime import datetime
from configs import DevelopmentConfig


def dict_to_orm(d, o):
    for k, v in d.items():
        if k == "password":
            o.password = v
        if k == "date":
            o.date = datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        else:
            try:
                setattr(o, k, v or None)
            except:
                print(f"{k}-{v}-{d}")
                exit


def csv_to_databases(path, orm):
    with open(path, encoding="utf-8") as file:
        for d in csv.DictReader(file):
            o = orm()
            dict_to_orm(d, o)
            db.session.add(o)
            db.session.flush()
        db.session.commit()


def register_script(app: Flask):
    # 用于注册一个命令到Flask应用程序的命令行界面（CLI）
    # 这个命令是 init，用于初始化数据库
    @app.cli.command()  # 装饰器，将 init 函数注册为 Flask CLI 命令
    def init():
        # 删除所有数据库
        db.drop_all()
        # 创建数据库
        db.create_all()

        root = current_app.config.get("ROOT_PATH")

        rights_data_path = os.path.join(root, "static", "data", "ums_rights.csv")
        csv_to_databases(rights_data_path, RightsORM)

        role_data_path = os.path.join(root, "static", "data", "ums_role.csv")
        csv_to_databases(role_data_path, RoleORM)

        with open(role_data_path, encoding="utf-8") as file:
            for d in csv.DictReader(file):
                role: RoleORM = RoleORM.query.get(d["id"])
                id_list = [int(_id) for _id in d["rights_ids"].split(":")]
                role.rights_list = RightsORM.query.filter(
                    RightsORM.id.in_(id_list)
                ).all()
                db.session.commit()

        department_data_path = os.path.join(
            root, "static", "data", "ums_department.csv"
        )
        csv_to_databases(department_data_path, DepartmentORM)

        user_data_path = os.path.join(root, "static", "data", "ums_user.csv")
        csv_to_databases(user_data_path, UserORM)

        with open(user_data_path, encoding="utf-8") as file:
            for d in csv.DictReader(file):
                user: UserORM = UserORM.query.get(d["id"])
                id_list = [int(_id) for _id in d["role_ids"].split(":")]
                user.role_list = RoleORM.query.filter(RoleORM.id.in_(id_list)).all()
                db.session.commit()

        ponding_data_path = os.path.join(root, "static", "data", "ums_data_ponding.csv")
        csv_to_databases(ponding_data_path, DataPondingORM)

        channels_data_path = os.path.join(
            root, "static", "data", "ums_task_channels.csv"
        )
        csv_to_databases(channels_data_path, ChannelsORM)

        try:
            DevelopmentConfig.SCHEDULER_JOBSTORES.get("default").remove_all_jobs()
        except Exception as e:
            print(f"{e}")
