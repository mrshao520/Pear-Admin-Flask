from flask import Blueprint, request
from flask_sqlalchemy.pagination import Pagination
from pear_admin.extensions import db
from pear_admin.orms import DataPondingORM, DataSummaryORM
from datetime import datetime
from operator import or_, and_

ponding_api = Blueprint("ponding", __name__)


@ponding_api.get("/ponding")
def ponding_list():
    page = request.args.get("page", default=-1, type=int)
    per_page = request.args.get("limit", default=10, type=int)

    id = request.args.get("id", default=None, type=int)
    city = request.args.get("city", default=None, type=str)
    start_datetime = request.args.get("start_datetime", default=None, type=str)
    end_datetime = request.args.get("end_datetime", default=None, type=str)
    if start_datetime:
        start_datetime = datetime.strptime(start_datetime, "%Y-%m-%d %H:%M:%S")
    else:
        start_datetime = datetime.strptime("2010-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    if end_datetime:
        end_datetime = datetime.strptime(end_datetime, "%Y-%m-%d %H:%M:%S")
    else:
        end_datetime = datetime.now()

    if page > 0:
        # 分开查询，简单
        if id:
            q = db.select(DataPondingORM).where(DataPondingORM.id == id)
        elif city:
            q = (
                db.select(DataPondingORM)
                .where(DataPondingORM.city == city)
                .where(DataPondingORM.date > start_datetime)
                .where(DataPondingORM.date < end_datetime)
            )
        else:
            q = (
                db.select(DataPondingORM)
                .where(DataPondingORM.date > start_datetime)
                .where(DataPondingORM.date < end_datetime)
            )

        pages: Pagination = db.paginate(q, page=page, per_page=per_page)

        return {
            "code": 0,
            "msg": "获取积水点数据成功",
            "data": [item.json() for item in pages.items],
            "count": pages.total,
        }
    else:

        if id:
            q = db.select(DataPondingORM).where(DataPondingORM.id == id)
        elif city:
            q = (
                db.select(DataPondingORM)
                .where(DataPondingORM.city == city)
                .where(DataPondingORM.date > start_datetime)
                .where(DataPondingORM.date < end_datetime)
            )
        else:
            q = (
                db.select(DataPondingORM)
                .where(DataPondingORM.date > start_datetime)
                .where(DataPondingORM.date < end_datetime)
            )

        ponding_all = db.session.execute(q).scalars()
        # for p in ponding_all:
        #     print(p)
        data = [item.json() for item in ponding_all]
        return {
            "code": 0,
            "msg": "获取积水点数据成功",
            "data": data,
            "count": len(data),
        }


@ponding_api.post("/ponding")
def create_ponding():
    data = request.get_json()
    if data["id"]:
        del data["id"]
    # print(data)
    # {'id': None, 'date': '2024-06-18 14:49:56', 'time': '11', 'city': '11',
    # 'position': '11', 'lati_longi_tude': '11', 'depth_value': '1', 'description': '1'}
    date = datetime.strptime(data.get("date"), "%Y-%m-%d %H:%M:%S")
    data["date"] = date
    ponding = DataPondingORM(**data)
    result = ponding.save()
    if result:
        return {"code": 0, "msg": "新增积水点信息成功"}
    else:
        return {"code": -1, "msg": "重复数据，插入失败"}, 401


@ponding_api.put("/ponding/<int:uid>")
def change_ponding(uid):
    """修改

    Args:
        uid (_type_): id
    """
    data = request.get_json()
    del data["id"]

    ponding_obj = DataPondingORM.query.get(uid)
    for key, value in data.items():
        if key == "date":
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        setattr(ponding_obj, key, value)
    result = ponding_obj.save()
    if result:
        return {"code": 0, "msg": "修改积水点信息成功"}
    else:
        return {"code": -1, "msg": "修改积水点信息失败，数据重复"}, 401


@ponding_api.delete("/ponding/<int:rid>")
def del_ponding(rid):
    """删除

    Args:
        rid (_type_): id
    """
    # print(f'删除 ： {rid}')
    ponding_obj = DataPondingORM.query.get(rid)
    ponding_obj.delete()
    return {"code": 0, "msg": f"删除行 [id:{rid}] 成功"}
