#!/bin/bash

# Wait for MySQL container to be ready
echo "Waiting for MySQL container to start..."
# 尝试连接到主机名为mysql的MySQL服务器，使用用户名为root，密码为123456，
# ";" 并且执行一个空语句（;）
# 2>/dev/null 将错误输出重定向到 /dev/null ，即丢弃错误信息
until mysql -h mysql -uroot -p123456 -e ";" 2>/dev/null; do
# until mysql -h mysql -uroot -p123456 -e ; do
    echo "MySQL container not ready, sleeping for 5 seconds..."
    sleep 5
done
echo "MySQL container started successfully!"

# to start create the dababase
echo " start to create the databse... "
mysql -uroot -p123456 -hmysql -e 'CREATE DATABASE PearAdminFlask DEFAULT CHARSET UTF8;'


# Initialize Flask database
echo "Initializing Flask database..."
flask db init
flask db migrate
flask db upgrade
flask admin init

# Start gunicorn application
echo "Starting gunicorn application..."
exec gunicorn -c gunicorn.conf.py "applications:create_app()"