import requests
test_url = "https://sheetdb.io/api/v1/k12fpa1q0mb72"
test_data = {
    "data": [{
        "Time": "الاختبار الأول",
        "User_ID": "12345",
        "Full_Name": "محمود أبو الفضل",
        "Username": "@test",
        "Bot_User": "@Bot",
        "Bot_Token": "Token_Test"
    }]
}
r = requests.post(test_url, json=test_data)
print(f"الحالة: {r.status_code}, الرد: {r.text}")