from datetime import datetime
import subprocess
import requests
import csv
import json

from .get_location import get_location
from configs import BaseConfig
from pear_admin.extensions import db
from pear_admin.orms import DataPondingORM, ChannelsORM
from pear_admin.extensions import scheduler


def task_function(
    channels: str, city: str, start_datetime: datetime, end_datetime: datetime
):
    print(f"{datetime.now()}-{channels}-{city}-{start_datetime}-{end_datetime}")

    untreated_filename = BaseConfig.UNTREATED_FILENAME
    csv_filename = BaseConfig.CSV_FILENAME
    csv_headers = BaseConfig.CSV_HEADERS

    with scheduler.app.app_context():
        channel_info = db.session.query(ChannelsORM).filter_by(channel=channels).first()

    if channel_info is None:
        return False

    command = channel_info.command.split(" ")
    replace_words = ["city", "start_datetime", "end_datetime"]
    new_words = [
        city,
        start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
    ]
    command_list = [
        new_words[replace_words.index(word)] if word in replace_words else word
        for word in command
    ]

    print(f"command list : {command_list}")

    results = []
    errors = []
    p = None

    try:
        p = subprocess.Popen(
            args=command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # 获取实时输出
        for line in iter(p.stdout.readline, b""):
            line_info = line.decode("utf-8").strip()
            print("output:" + line_info)
            results.append(line_info)
        for line in iter(p.stderr.readline, b""):
            line_info = line.decode("utf-8").strip()
            print("error:" + line_info)
            errors.append(line_info)
        # 等待命令执行完成
        p.wait()
        print(f"results length : {len(results)}")
        print(f"errors  length : {len(errors)}")
    except Exception as e:
        print(f"Command '{command_list}' throw an exception: {e}")
        channel_info.information = repr(e)
    finally:
        if p:
            # 确保子进程资源被释放
            p.stdout.close()
            p.stderr.close()
            p.terminate()

    if len(results) == 0 and len(errors) > 0:
        channel_info.status = False
        channel_info.information = errors[-1]
    elif len(results) > 0 and len(errors) > 0:
        channel_info.information = errors[-1]

    if len(results) == 0:
        with scheduler.app.app_context():
            channel_info.save()
        return True

    channel_info.total_number += len(results)

    if not BaseConfig.OPEN_PONDING_SERVER:
        # 关闭 gpu 处理任务
        with open(untreated_filename, "a", newline="", encoding="utf-8") as file:
            file.write("\n".join(results))
        pass
    else:
        effective_number = 0
        # 打开 gpu 处理任务
        req_extract_url = BaseConfig.PONDING_EXTRACT
        req_headers = {"Content-type": "application/json;charset=UTF-8"}
        req_json_str = json.dumps({"city": city, "content": results})
        extract_res = requests.post(
            req_extract_url, json=req_json_str, headers=req_headers
        )
        extract_res_json = json.loads(extract_res.text)
        if extract_res_json["status"] != "success":
            with scheduler.app.app_context():
                channel_info.save()
            return False
        for info in extract_res_json["info"]:
            print(info)
            lati_longi_tude = get_location(city=info["city"], address=info["position"])
            if not lati_longi_tude:
                # 未获取经纬度
                continue
            longitude, latitude = lati_longi_tude.split(",", maxsplit=2)
            info["longitude"] = longitude
            info["latitude"] = latitude
            info["date"] = datetime.strptime(info["date"], "%Y-%m-%d %H:%M:%S")
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

                print("保存成功")
                effective_number += 1
            else:
                print("保存失败")
                # 保存失败
                pass

        # 保存 渠道 信息
        with scheduler.app.app_context():
            channel_info.save()
        return True
