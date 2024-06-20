from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from pear_admin.extensions import db, scheduler
from pear_admin.orms import TaskORM
from datetime import datetime
from .task_function import task_function

import subprocess

task_api = Blueprint("task", __name__)


@task_api.get("/task")
def task_list():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("limit", default=10, type=int)

    q = db.select(TaskORM)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        "code": 0,
        "msg": "获取任务列表成功",
        "data": [item.json() for item in pages.items],
        "count": pages.total,
    }


@task_api.post("/task")
def create_task():
    # 获取数据
    data = request.get_json()
    id = data["id"]
    if data["id"]:
        del data["id"]
    # print(data)
    # {'id': None, 'date': '2024-06-18 14:49:56', 'time': '11', 'city': '11',
    # 'position': '11', 'lati_longi_tude': '11', 'depth_value': '1', 'description': '1'}
    # 转换时间格式
    data["start_datetime"] = datetime.strptime(
        data.get("start_datetime"), "%Y-%m-%d %H:%M:%S"
    )
    data["end_datetime"] = datetime.strptime(
        data.get("end_datetime"), "%Y-%m-%d %H:%M:%S"
    )
    data["interval"] = datetime.strptime(data.get("interval"), "%H:%M:%S")
    # 将城市拼接在一起
    cites = []
    for k, v in data.items():
        if v == "on":
            cites.append(k)
    for i in cites:
        del data[i]
    data["cities"] = ":".join(cites)
    # 保存任务
    task = TaskORM(**data)
    # save之后才能产生主键id
    task.save()
    # 增加定时任务
    scheduler.add_job(
        func=task_function,
        trigger="interval",
        id=str(task.id),
        kwargs={
            "channels": data["channels"],
            "city": data["cities"],
            "start_datetime": data["start_datetime"],
            "end_datetime": data["end_datetime"],
        },
        hours=data["interval"].hour,
        minutes=data["interval"].minute,
        seconds=data["interval"].second,
        start_date=data["start_datetime"],
        end_date=data["end_datetime"],
        # replace_existing=True,
    )

    return {"code": 0, "msg": "新增任务成功"}


@task_api.put("/task/<int:uid>")
def change_task(uid):
    """修改

    Args:
        uid (_type_): id
    """
    data = request.get_json()
    del data["id"]

    cites = []
    for k, v in data.items():
        if v == "on":
            cites.append(k)
    for i in cites:
        del data[i]
    data["cities"] = ":".join(cites)

    task_obj = TaskORM.query.get(uid)
    for key, value in data.items():
        if key == "start_datetime" or key == "end_datetime":
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            data[key] = value
        elif key == "interval":
            value = datetime.strptime(value, "%H:%M:%S")
            data[key] = value
        setattr(task_obj, key, value)

    # 修改定时任务
    if scheduler.get_job(str(task_obj.id)):
        # scheduler.remove_job(str(task_obj.id))
        # print(task_obj.id)
        scheduler.modify_job(
            id=str(task_obj.id),
            func=task_function,
            trigger="interval",
            kwargs={
                "channels": data["channels"],
                "city": data["cities"],
                "start_datetime": data["start_datetime"],
                "end_datetime": data["end_datetime"],
            },
            hours=data["interval"].hour,
            minutes=data["interval"].minute,
            seconds=data["interval"].second,
            start_date=data["start_datetime"],
            end_date=data["end_datetime"],
            # replace_existing=True,
        )

    task_obj.save()
    return {"code": 0, "msg": "修改任务成功"}


@task_api.delete("/task/<int:rid>")
def del_task(rid):
    """删除

    Args:
        rid (_type_): id
    """
    # print(f'删除 ： {rid}')
    task_obj = TaskORM.query.get(rid)
    # 删除定时任务
    if scheduler.get_job(str(task_obj.id)):
        scheduler.remove_job(str(task_obj.id))
    task_obj.delete()

    return {"code": 0, "msg": f"删除行 [id:{rid}] 成功"}
