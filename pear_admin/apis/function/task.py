from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from pear_admin.extensions import db
from pear_admin.orms import TaskORM
from datetime import datetime

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
    data = request.get_json()
    print(data)
    if data["id"]:
        del data["id"]
    # print(data)
    # {'id': None, 'date': '2024-06-18 14:49:56', 'time': '11', 'city': '11',
    # 'position': '11', 'lati_longi_tude': '11', 'depth_value': '1', 'description': '1'}
    data["start_datetime"] = datetime.strptime(
        data.get("start_datetime"), "%Y-%m-%d %H:%M:%S"
    )
    data["end_datetime"] = datetime.strptime(
        data.get("end_datetime"), "%Y-%m-%d %H:%M:%S"
    )
    data["interval"] = datetime.strptime(data.get("interval"), "%H:%M:%S")
    cites = []
    for k, v in data.items():
        if v == "on":
            cites.append(k)
    for i in cites:
        del data[i]
    data["cities"] = ":".join(cites)

    task = TaskORM(**data)
    task.save()
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
        elif key == "interval":
            value = datetime.strptime(value, "%H:%M:%S")
        setattr(task_obj, key, value)
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
    task_obj.delete()
    return {"code": 0, "msg": f"删除行 [id:{rid}] 成功"}
