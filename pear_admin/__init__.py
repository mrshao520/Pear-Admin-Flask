from flask import Flask, render_template

from configs import config
from pear_admin.apis import register_apis
from pear_admin.extensions import register_extensions
from pear_admin.orms import UserORM
from pear_admin.views import register_views


def create_app(config_name="dev"):
    # 创建一个名为"pear-admin-flask"的Flask应用实例
    app = Flask("pear-admin-flask")
    # 基于传入的配置名称（默认为"dev"开发环境），从配置字典中加载配置
    app.config.from_object(config[config_name])
    # 注册扩展（例如数据库、邮件服务等）到app实例
    register_extensions(app)
     # 注册API路由，定义URL到函数的映射
    register_apis(app)
    # 注册视图函数，定义如何处理HTTP请求
    register_views(app)
    
    global_app = app

    @app.errorhandler(403)
    def handle_404(e):
        return render_template("error/403.html")
    
    @app.errorhandler(404)
    def handle_403(e):
        return render_template("error/404.html")
    
    @app.errorhandler(500)
    def handle_500(e):
        return render_template("error/500.html")
    
    # 返回配置好的Flask应用实例
    return app
