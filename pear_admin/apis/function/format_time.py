import re
from datetime import datetime


def format_datetime(input_datetime: datetime, str_datetime: str):
    # 定义时间表达式的正则模式
    time_patterns = {
        # 年份+月份+日期
        r"(\d+)年(\d+)月(\d+)[日|号]": lambda year, month, day: datetime(
            year=year, month=month, day=day
        ),
        # 月份+日期
        r"(\d+)月(\d+)[日|号]": lambda month, day: datetime(
            year=input_datetime.year, month=month, day=day
        ),
        # 日期
        r"(\d+)[日|号]": lambda day: datetime(
            year=input_datetime.year, month=input_datetime.month, day=day
        ),
        r"今|当": lambda: input_datetime,
        r"昨": lambda: datetime(
            year=input_datetime.year,
            month=input_datetime.month,
            day=input_datetime.day - 1,
        ),
        r"明": lambda: datetime(
            year=input_datetime.year,
            month=input_datetime.month,
            day=input_datetime.day + 1,
        ),
        r"(\d{4})-(\d{2})-(\d{2})": lambda year, month, day: datetime(year, month, day),
        r"(\d{2})-(\d{2})": lambda month, day: datetime(
            input_datetime.year, month, day
        ),
        r"(\d{4})/(\d{2})/(\d{2})": lambda year, month, day: datetime(year, month, day),
        r"(\d{2})/(\d{2})": lambda year, month, day: datetime(
            input_datetime.year, month, day
        ),
    }

    # 解析时间表达式
    for pattern, func in time_patterns.items():
        match = re.search(pattern, str_datetime)
        # print(str_datetime)
        if match:
            match = [int(m) for m in match.groups()]
            return func(*match)
    return None


if __name__ == "__main__":
    # 测试
    texts = [
        "2月19日晚至20日凌晨",
        "今天上午",
        "11日17时至13日0时",
        "截至12点",
        "7月29日下午2时许",
        "7月31日一大早",
        "今天上午",
        "昨天早上5时许",
        "今天上午9时",
        "9月7日夜间到8日早晨",
        "28日10时至14时",
        "昨天（7月11日）",
        "昨天早上",
        "2月19日晚至20日凌晨",
        "截至7月29日中午11时30分",
    ]

    for text in texts:
        now = datetime.now()
        result = format_datetime(now, text)
        print(f"{now}       {result}")
