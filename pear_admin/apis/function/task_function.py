from datetime import datetime, timedelta
import subprocess
import requests
import csv
import json
import re
from loguru import logger
from .get_location import get_location
from configs import BaseConfig
from pear_admin.extensions import db
from pear_admin.orms import DataPondingORM, ChannelsORM
from pear_admin.extensions import scheduler
from .format_time import format_datetime


def task_function(
    id: str,
    channels: str,
    city: str,
    interval: str,
    start_datetime: datetime,
    end_datetime: datetime,
    task_start_datetime: datetime,
    task_end_datetime: datetime,
):
    now = datetime.now()
    logger.info(f"当前时间: {now} --- 任务id: {id}")
    logger.info(f"任务开始结束时间: {task_start_datetime} --- {task_end_datetime}")
    # 如果不设置开始结束，则取当天凌晨和明天凌晨
    if not start_datetime:
        start_datetime = datetime(year=now.year, month=now.month, day=now.day)

    if not end_datetime:
        end_datetime = datetime(
            year=now.year, month=now.month, day=now.day
        ) + timedelta(days=1)

    logger.info(f"爬虫开始结束时间: {start_datetime} --- {end_datetime}")
    logger.info(f"城市: {city} --- 渠道: {channels} --- 间隔时间: {interval}")

    # 配置文件，保存的文件路径
    untreated_filename = BaseConfig.UNTREATED_FILENAME
    csv_filename = BaseConfig.CSV_FILENAME
    csv_headers = BaseConfig.CSV_HEADERS

    # 获取检索通道配置
    with scheduler.app.app_context():
        channel_info = db.session.query(ChannelsORM).filter_by(channel=channels).first()

    if channel_info is None:
        logger.info(f"未找到对应渠道: {channels}")
        return False
    # 根据命令格式进行替换
    command = channel_info.command.split(" ")
    replace_words = ["city", "start_datetime", "end_datetime"]
    new_words = [
        city,
        start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    ]
    command_list = [
        (new_words[replace_words.index(word)] if word in replace_words else word)
        for word in command
        if word != ""
    ]
    logger.info(f"command list : {command_list}")

    if len(command_list) == 0:
        # 空命令
        logger.info(f"空命令，返回!")
        return

    # 开启子进程进行爬取
    results = []  # 输出结果
    errors = []  # 错误信息
    p = None
    try:
        p = subprocess.Popen(
            args=command_list[1:],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=command_list[0],
        )
        # 获取实时输出
        for line in iter(p.stdout.readline, b""):
            line_info = line.decode("utf-8").strip()
            logger.info("output:" + line_info)
            results.append(line_info)
        for line in iter(p.stderr.readline, b""):
            line_info = line.decode("utf-8").strip()
            logger.debug("error:" + line_info)
            errors.append(line_info)
        # 等待命令执行完成
        p.wait()
        logger.info(f"results length : {len(results)}")
        logger.debug(f"errors  length : {len(errors)}")
    except Exception as e:
        logger.info(f"Command '{command_list}' throw an exception: {e}")
        channel_info.information = f"Command '{command_list}' throw an exception: {e}"
    finally:
        if p:
            # 确保子进程资源被释放
            p.stdout.close()
            p.stderr.close()
            p.terminate()

    if len(results) == 0 and len(errors) > 0:
        # 未爬取到信息，且报错，说明爬虫有问题
        channel_info.status = False
        channel_info.information = errors[-1]
    elif len(results) > 0 and len(errors) > 0:
        # 爬取到信息，但是报错
        channel_info.information = errors[-1]

    if len(results) == 0:
        # 未爬取到信息，返回
        logger.info("未爬取到有用信息，返回!")
        with scheduler.app.app_context():
            channel_info.save()
        return True

    # 记录爬取的总数
    channel_info.total_number += len(results)
    logger.info(f"渠道 {channels} 的爬取总数: {channel_info.total_number}")

    if not BaseConfig.OPEN_PONDING_SERVER:
        # 关闭 gpu 处理任务，将提取到的信息保存到文件中
        logger.info(f"关闭 gpu 处理任务，将爬取到的信息保存到文件中")
        with open(untreated_filename, "a", newline="", encoding="utf-8") as file:
            file.write("\n".join(results))
        pass
    else:
        effective_number = 0
        # 打开 gpu 处理任务
        req_extract_url = BaseConfig.PONDING_EXTRACT
        req_headers = {"Content-type": "application/json;charset=UTF-8"}
        req_json_str = json.dumps({"city": city, "content": results})
        try:
            extract_res = requests.post(
                req_extract_url, json=req_json_str, headers=req_headers
            )
            extract_res_json = json.loads(extract_res.text)
        except Exception as e:
            print(f"request to ponding_server get an error: {e}")
            with scheduler.app.app_context():
                channel_info.save()
            return False

        if extract_res_json["status"] != "success":
            logger.debug(f"提取失败:{extract_res_json['info']}")
            with scheduler.app.app_context():
                channel_info.save()
            return False
        for info in extract_res_json["info"]:
            logger.info(info)
            # 获取经纬度
            lati_longi_tude = get_location(city=info["city"], address=info["position"])
            if not lati_longi_tude:
                # 未获取经纬度
                logger.info(f"未获取经纬度!")
                continue
            longitude, latitude = lati_longi_tude.split(",", maxsplit=2)
            info["longitude"] = longitude
            info["latitude"] = latitude
            logger.info(f"经纬度: {longitude},{latitude}")
            # 转化时间
            info["date"] = datetime.strptime(info["date"], "%Y-%m-%d %H:%M:%S")
            # 格式化积水深度值
            info["format_depth_value"] = format_value(info["depth_value"])
            # 格式化时间
            info["format_time"] = format_datetime(info["date"], info["time"])
            # 保存到数据库
            with scheduler.app.app_context():
                ponding = DataPondingORM(**info)
                result = ponding.save()
                ponding_json = ponding.json()
            if result:
                ponding_list = [ponding_json[header] for header in csv_headers]
                # 打开CSV文件
                with open(
                    csv_filename, mode="a", newline="", encoding="utf-8"
                ) as csvfile:
                    # 创建CSV写入器
                    writer = csv.writer(csvfile)
                    # 如果CSV文件不存在，则写入列名
                    if not csvfile.tell():
                        writer.writerow(csv_headers)
                    # 写入数据
                    writer.writerow(ponding_list)

                # print("保存成功")
                # logger.info("保存成功")
                effective_number += 1
            else:
                # print("保存失败，重复数据")
                logger.info("保存失败，重复数据")
                # 保存失败
                pass
        channel_info.total_effective_number += effective_number
        logger.info(f"爬取有效信息个数/总有效信息个数: {effective_number}/{channel_info.total_effective_number}")
        # 保存 渠道 信息
        with scheduler.app.app_context():
            channel_info.save()
        return True


def format_value(depth: str):
    numbers = re.findall(r"\d+\.\d+|\d+", depth)
    # print(numbers)
    if not numbers:
        return
    number = int(numbers[0])  # 获取第一个数字
    if "cm" in depth or "CM" in depth or "厘米" in depth or "公分" in depth:
        return f"{number}cm"
    if "mm" in depth or "MM" in depth or "毫米" in depth:
        return f"{number // 100}cm"
    elif "m" in depth or "M" in depth or "米" in depth:
        return f"{number * 100}cm"
    return
