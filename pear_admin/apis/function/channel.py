from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from pear_admin.extensions import db, scheduler
from pear_admin.orms import ChannelsORM
from datetime import datetime

channel_api = Blueprint("channel", __name__)


@channel_api.get("/channel")
def channel_list():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("limit", default=10, type=int)

    q = db.select(ChannelsORM)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        "code": 0,
        "msg": "获取检索列表成功",
        "data": [item.json() for item in pages.items],
        "count": pages.total,
    }


@channel_api.post("/channel")
def create_channel():
    # 获取数据
    data = request.get_json()
    id = data["id"]
    if data["id"]:
        del data["id"]
    
    # data["end_datetime"] = datetime.strptime(
    #     data.get("end_datetime"), "%Y-%m-%d %H:%M:%S"
    # )
    
    # 保存任务
    channel = ChannelsORM(**data)
    # save之后才能产生主键id
    channel.save()

    return {"code": 0, "msg": "新增检索成功"}


@channel_api.put("/channel/<int:uid>")
def change_channel(uid):
    """修改

    Args:
        uid (_type_): id
    """
    data = request.get_json()
    del data["id"]

    channel_obj = ChannelsORM.query.get(uid)
    for key, value in data.items():
        setattr(channel_obj, key, value)

    channel_obj.save()
    return {"code": 0, "msg": "修改检索成功"}


@channel_api.delete("/channel/<int:rid>")
def del_channel(rid):
    """删除

    Args:
        rid (_type_): id
    """
    channel_obj = ChannelsORM.query.get(rid)
    channel_obj.delete()

    return {"code": 0, "msg": f"删除行 [id:{rid}] 成功"}

