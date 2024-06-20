from datetime import datetime
import subprocess
import requests
import json
from .get_location import get_location


def task_function(channels, city, start_datetime, end_datetime):
    print(f"{datetime.now()}-{channels}-{city}-{start_datetime}-{end_datetime}")
    args = ["cat", "test.txt"]
    results = []
    errors = []
    
    try:
        p = subprocess.Popen(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
        print(f"Command '{args}' throw an exception: {e}")
    finally:
        # 确保子进程资源被释放
        p.stdout.close()
        p.stderr.close()
        p.terminate()

    req_headers = {"Content-type": "application/json;charset=UTF-8"}
    req_json_str = json.dumps({"city": city, "content": results})
    extract_res = requests.post("http://127.0.0.1:8886/extract", json=req_json_str, headers=req_headers)
    extract_res_json = json.loads(extract_res.text)
    print(extract_res_json["info"])
    
