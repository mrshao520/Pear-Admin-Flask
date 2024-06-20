from pear_admin.extensions import db
from sqlalchemy import select
from ._base import BaseORM


class DataPondingORM(BaseORM):
    __tablename__ = "ums_data_ponding"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增id")
    date = db.Column(db.DateTime, nullable=False, comment="日期")
    time = db.Column(db.String(64), nullable=True, comment="时间")
    city = db.Column(db.String(64), nullable=False, comment="城市")
    position = db.Column(db.String(128), nullable=False, comment="地点")
    longitude = db.Column(db.String(64), nullable=False, comment="经度")
    latitude = db.Column(db.String(64), nullable=False, comment="纬度")
    depth_value = db.Column(db.String(64), nullable=True, comment="深度值")
    description = db.Column(db.String(256), nullable=True, comment="备注")

    def save(self):
        existing = (
            db.session.query(DataPondingORM)
            .filter_by(
                date=self.date,
                city=self.city,
                position=self.position,
            )
            .first()
        )
        if existing is None:
            # 如果不存在进行插入
            db.session.add(self)
            db.session.commit()
            return True
        else:
            # 数据存在
            return False
        # db.session.add(self)
        # db.session.commit()

    def __repr__(self) -> str:
        return f"Ponding(id={self.id!r}, date={self.date!r}, time={self.time!r} \
, city={self.city!r}, position={self.position!r} \
, longitude={self.longitude!r} \
, latitude={self.latitude!r} \
, depth_value={self.depth_value!r} \
, description={self.description!r})"

    def json(self):
        # print(self.date)
        return {
            "id": self.id,
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "time": self.time,
            "city": self.city,
            "position": self.position,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "depth_value": self.depth_value,
            "description": self.description,
        }


class DataSummaryORM(BaseORM):
    __tablename__ = "ums_data_summary"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="自增id")
    city = db.Column(db.String(64), nullable=False, comment="城市")
    description = db.Column(db.String(64), nullable=False, comment="描述")
    volume = db.Column(db.Integer, nullable=False, comment="容量")

    def __repr__(self) -> str:
        return f"SummaryTable(id={self.id!r}, city={self.city!r} \
, description={self.description!r}, volume={self.volume!r})"

    def json(self):
        return {
            "id": self.id,
            "city": self.city,
            "description": self.description,
            "volume": self.volume,
        }
