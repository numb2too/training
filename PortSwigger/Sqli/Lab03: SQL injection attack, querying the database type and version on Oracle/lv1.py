# 第一階段先能訪問成功
import requests
from typing import Optional, Any

BASE_URL="https://0ace00f50454eab380361caa00c80090.web-security-academy.net/filter"

"""
這邊發現Session()的S要大寫
雖然session的方法點進去也是直接呼叫Session()
但AI表示大寫比較常見, 官方好像也都用大寫
"""
session = requests.Session()

def send_get_request(url:str, params: dict[str,Any], timeout:int = 10) -> Optional[requests.Response]:
    try:
        return session.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None;

def main():
    response = send_get_request(BASE_URL, {"category": "Gifts"})
    if response and response.status_code == 200:
        print("connect success")
    else:
        print("connect failed")

if __name__ == "__main__":
    main()