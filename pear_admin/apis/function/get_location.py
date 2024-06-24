import requests
from configs import BaseConfig


def get_location(city, address, output="JSON", sig=None, callback=None):
    """
    调用高德地图API获取地理编码信息中的位置

    :param city: 指定查询的城市
    :param address: 结构化地址信息
    :param output: 返回数据格式类型，默认为'JSON'
    :param sig: 数字签名，可选
    :param callback: 回调函数，可选
    :return: 地理编码信息中的location字段
    """
    base_url = "https://restapi.amap.com/v3/geocode/geo"  # API的基础URL
    params = {
        "key": BaseConfig.GAODE_API,
        "address": address,
        "city": city,
        "output": output,
    }
    if sig:
        params["sig"] = sig
    if callback:
        params["callback"] = callback

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        # 解析JSON响应内容
        data = response.json()
        # 检查响应中的status字段是否表示成功
        if data["status"] == "1" and "geocodes" in data and len(data["geocodes"]) > 0:
            # 返回第一个geocode对象中的location字段
            return data["geocodes"][0]["location"]
        else:
            # return f"Error: {data.get('info', 'No info provided')}"
            return False
    else:
        # return f'HTTP Error: {response.status_code}'
        return False


if __name__ == "__main__":
    city_name = "广州"
    address_name = "天河区石溪村东村街"
    location = get_location(city=city_name, address=address_name)
    city = get_location(city=None, address=city_name)
    print(location)
    print(city)
