from flask import redirect
from flask_jwt_extended import JWTManager

from pear_admin.orms.user import UserORM

# JSON Web Token 认证机制
# 创建 JWTManager类的实例，处理JWT的中央对象
jwt = JWTManager()

"""
装饰器user_identity_loader用于定义当JWT验证成功后，
如何从用户对象中加载用户身份。函数user_identity_lookup将被调用，
并传入一个user对象作为参数。这个函数返回user对象的id作为用户身份。 
"""
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

""" 
装饰器user_lookup_loader用于定义当JWT验证需要查找用户身份时，如何从数据库中查找对应的UserORM对象。
函数user_lookup_callback将被调用，并传入jwt_header和jwt_data作为参数。
这个函数通过jwt_data中的sub字段（通常是用户ID）来查询数据库，并返回匹配的用户对象。 
"""
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserORM.query.filter(UserORM.id == identity).one_or_none()


""" 
装饰器expired_token_loader用于定义当JWT过期时，返回给客户端的响应。
函数expired_token_callback将被调用，这个函数返回一个包含错误消息和错误码的字典，
以及HTTP状态码403（禁止）。 
"""
@jwt.expired_token_loader
def expired_token_callback():
    return {"msg": "token 已过期，请重新登录", "code": -1}, 403

""" 
装饰器unauthorized_loader用于定义当请求缺少有效的JWT时，返回给客户端的响应。
函数missing_token_callback将被调用，这个函数返回一个包含错误消息和错误码的字典，
以及HTTP状态码403（禁止）。 
"""
@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"msg": "操作未授权，请重新登录", "code": -1}, 403
