from pear_admin.extensions import db
from ._base import BaseORM


class TaskORM(BaseORM):
    __tablename__ = "ums_task"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增id")
    name = db.Column(db.String(64), nullable=False, comment="任务名")
    cities = db.Column(db.String(256), nullable=False, comment="城市")
    channels = db.Column(db.String(64), nullable=False, comment="检索渠道")
    interval = db.Column(db.DateTime, nullable=False, comment="时间间隔")
    start_datetime = db.Column(db.DateTime, nullable=True, comment="开始时间")
    end_datetime = db.Column(db.DateTime, nullable=True, comment="结束时间")
    task_start_datetime = db.Column(db.DateTime, nullable=False, comment="任务开始时间")
    task_end_datetime = db.Column(db.DateTime, nullable=False, comment="任务开始时间")
    description = db.Column(db.String(256), nullable=True, comment="任务描述")

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "cities": self.cities,
            "channels": self.channels,
            "interval": self.interval.strftime("%H:%M:%S"),
            "start_datetime": (
                self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
                if self.start_datetime
                else ""
            ),
            "end_datetime": (
                self.end_datetime.strftime("%Y-%m-%d %H:%M:%S")
                if self.end_datetime
                else ""
            ),
            "task_start_datetime": self.task_start_datetime.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "task_end_datetime": self.task_end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "description": self.description,
        }
