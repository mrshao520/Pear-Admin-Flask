from collections import OrderedDict
from copy import deepcopy

from flask import Blueprint, make_response, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    jwt_required,
)

from pear_admin.extensions import db
from pear_admin.orms import RightsORM, RoleORM, UserORM

passport_api = Blueprint("passport", __name__)


@passport_api.post("/login")
def login_in():
    data = request.get_json()
    # print(f'data : {data}')
    # data : {'username': '正心全栈编程', 'password': '123456'}
    user: UserORM = db.session.execute(
        db.select(UserORM).where(UserORM.username == data["username"])
    ).scalar()

    if not user:
        return {"msg": "用户不存在", "code": -1}, 401
    if not user.check_password(data["password"]):
        return {"msg": "用户密码错误", "code": -1}, 401

    # 访问令牌，用于验证用户的一次性请求
    # 生成一个包含用户身份信息的JWT令牌。这个访问令牌会在用户登录后提供给客户端，用于在后续的请求中验证用户身份。
    access_token = create_access_token(user)
    # 刷新令牌，用于请求新的访问令牌
    # 生成一个用于刷新访问令牌的JWT令牌。当访问令牌过期时，用户可以使用刷新令牌来获取一个新的访问令牌。
    refresh_token = create_refresh_token(user)

    response = make_response(
        {
            "code": 0,
            "msg": "登录成功",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )

    return response


@passport_api.route("/logout", methods=["GET", "POST"])
@jwt_required()
def logout():
    return {"msg": "退出登录成功", "code": 0}


# 指定 get 请求的路由 /menu
@passport_api.get("/menu")
# 要求访问的路由必须提供一个有效的JWT
# 否则返回 401 Unauhorized 错误
@jwt_required()
def menus_api():
    # 创建一个空集合，用于存储当前用户的所有权限
    rights_orm_list = set()
    # 调用get_current_user()函数获取当前登录的用户对象。
    current_user: UserORM = get_current_user()
    # print(f'{current_user.json()}')
    """ 
    {
        'id': 3, 
        'username': '正心全栈编程', 
        'nickname': 'zhengxinonly', 
        'mobile': '18675867241', 
        'email': 'pyxxponly@gmail.com', 
        'create_at': '2024-06-16 07:00:46'
    }
    """
    # 遍历当前用户的所有角色
    for role in current_user.role_list:
        # 遍历每个角色的所有权限
        for rights_orm in role.rights_list:
            # 检查权限的类型，如果权限类型不是"auth"，则将其添加到rights_orm_list集合中。
            if rights_orm.type != "auth":
                # auth是权限，不是左侧功能栏
                rights_orm_list.add(rights_orm)
    # print(rights_orm_list)
    # {<RightsORM 111>, <RightsORM 116>, <RightsORM 125>, <RightsORM 126>, <RightsORM 100>, <RightsORM 124>, <RightsORM 106>, <RightsORM 101>}
    # 将权限对象转换成json，并创建一个列表
    rights_list = [rights_orm.menu_json() for rights_orm in rights_orm_list]
    
    # 根据父ID和ID对菜单列表进行排序。
    rights_list.sort(key=lambda x: (x["pid"], x["id"]), reverse=True)
        
    menu_dict_list = OrderedDict()
    for menu_dict in rights_list:
        if menu_dict["id"] in menu_dict_list.keys():  # 如果当前节点已经存在与字典中
            # 当前节点添加子节点
            menu_dict["children"] = deepcopy(menu_dict_list[menu_dict["id"]])
            menu_dict["children"].sort(key=lambda item: item["sort"])
            # 删除子节点
            del menu_dict_list[menu_dict["id"]]

        if menu_dict["pid"] not in menu_dict_list:
            menu_dict_list[menu_dict["pid"]] = [menu_dict]
        else:
            menu_dict_list[menu_dict["pid"]].append(menu_dict)

    result = sorted(menu_dict_list.get(0), key=lambda item: item["sort"])
    return result
