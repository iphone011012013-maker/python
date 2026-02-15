import requests

filename = input("[+] Enter List :")
print("[!] Start Check Emails Just Wait ... [!]")
email1 = [line.strip() for line in open(f"{filename}")]
for emails in email1:
    url = f'https://gmailcheck.pythonanywhere.com/?gmail={emails}'
    req = requests.get(url)
    getav = req.json()["check"]
    print(f"{emails}"+ " : "+getav)