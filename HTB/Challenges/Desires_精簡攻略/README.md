

### 測試方式
1. 用`py_test/zip_test/main.py`產生`payload.zip`
2. 用`py_test/tar_test/main.py`產生`payload.tar`
3. 用`main.go`確認`static`成功建立`.txt`檔案
> 注意`static`資料夾要確認有先建好
4. 用`exploit_test.py`確認目標server有成功建立`test.txt`
```!
Successfully created user 'user' with password 'user'
Successfully loggend in for user 'user' with password 'user'
Successfully uploaded archive!
Successfully got /static/test.txt!
```
### flag取得方法1
可直接用`auto_get_flag.py`取得flag

### flag取得方法2
1. `get_session_id.py`取得三組session
```!
THE DATE HEADER: Wed, 10 Sep 2025 04:45:32 GMT
THE DATETIME OBJECT: 2025-09-10 04:45:32+00:00
THE POSIX TIME: 1757479532

THE BEFORE HASH IS 515d6aa784d0035f48134983d379c75eaaf1125b557f643ee0c6bc580b163d00
THE EXACT HASH IS a6d42edf8d4b432a08868aa5c19c96c8aa7ca3d7bba513a4d1e0a56560f6344b
THE AFTER HASH IS 4c27a6a91183f3adb9e6c25fadcdb50d1da5e028b16cec2ca2d37e078beac8b9
```
2. `create_malicious_tar.py`創建`payload.tar`
3. `upload_malicious_tar.py`確認payload成功上傳到目標server
```!
Successfully created user 'normal1' with password 'normal1'
Successfully loggend in for user 'normal1' with password 'normal1'
Successfully uploaded archive!
```
4. `get_flag.py`取得flag
```!
HTB{flag}
```

