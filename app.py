from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

def calculate_entropy(password):
    """
    حساب الإنتروبي (Entropy) بناءً على منهج علمي.
    الإنتروبي = طول الكلمة * لوغاريتم(مساحة الاحتمالات) للأساس 2
    """
    pool_size = 0
    if any(c.islower() for c in password): pool_size += 26
    if any(c.isupper() for c in password): pool_size += 26
    if any(c.isdigit() for c in password): pool_size += 10
    if any(c in "!@#$%^&*()-_=+[]{};:,.<>/?|" for c in password): pool_size += 32
    
    if pool_size == 0: return 0
    
    entropy = len(password) * math.log2(pool_size)
    return round(entropy, 2)

def estimate_crack_time(entropy):
    """
    تقدير الوقت لكسر كلمة المرور بافتراض هجوم Brute Force سريع
    (10 مليار محاولة في الثانية - افتراض لأجهزة قوية حديثة)
    """
    guesses = 2 ** entropy
    seconds = guesses / 10_000_000_000  # 10 Billion guesses/sec
    
    if seconds < 1: return "أقل من ثانية (فوري)"
    if seconds < 60: return f"{round(seconds)} ثانية"
    if seconds < 3600: return f"{round(seconds/60)} دقيقة"
    if seconds < 86400: return f"{round(seconds/3600)} ساعة"
    if seconds < 31536000: return f"{round(seconds/86400)} يوم"
    if seconds < 3153600000: return f"{round(seconds/31536000)} سنة"
    return "قرون (آمنة جداً)"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    password = data.get('password', '')
    
    entropy = calculate_entropy(password)
    crack_time = estimate_crack_time(entropy)
    
    # تصنيف القوة
    if entropy < 28: strength = "ضعيفة جداً (خطر)"
    elif entropy < 36: strength = "ضعيفة"
    elif entropy < 60: strength = "متوسطة"
    elif entropy < 128: strength = "قوية"
    else: strength = "فائقة القوة"

    return jsonify({
        'entropy': entropy,
        'crack_time': crack_time,
        'strength': strength
    })

if __name__ == '__main__':
    app.run(debug=True)