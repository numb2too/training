1. `get_session_id.py`取得三組session
2. `create_malicious_tar.py`製作payload.tar
3. `upload_malicious_tar.py`上傳tar
4. `KO.py`獲得flag


詳細原理還不太懂
後續有空再釐清

參考此文章解題
https://medium.com/@MachineEP/hackthebox-desires-challenge-write-up-89711f6bdcef

---
# 歷程記錄
## 第一次用GO
先建立main.go
發現沒法跑
找一下如何架設go環境
去官網下載個go安裝

再來執行
`go run main.go`
還是不行
```!
main.go:4:2: no required module provides package github.com/mholt/archiver/v3: go.mod file not found in current directory or any parent directory; see 'go help modules'
```
發現要先init
`go mod init demo`
換跑出另一個錯誤
```!
main.go:4:2: no required module provides package github.com/mholt/archiver/v3; to add it:
        go get github.com/mholt/archiver/v3
```
原來是沒有拉github
`go get github.com/mholt/archiver/v3`
終於"hello world"了
開始來測試

## 測試階段
用`py/test1.py`產生`py/payload.zip`
在用`main.go`測試
果然如原作一樣
```!
[ERROR] Reading file in zip archive: checking path traversal attempt: illegal file path: ../../static/test.txt
```
