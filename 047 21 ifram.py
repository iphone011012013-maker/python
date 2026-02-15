import webview
import threading
import time

# دالة لتحديث العنوان
def get_current_url(window):
    while True:
        try:
            # محاولة الحصول على الرابط الحالي (قد لا تدعمها كل النسخ)
            current_url = window.get_current_url()
            print(f"Tracking: {current_url}")
        except:
            pass
        time.sleep(2)

def start_browser():
    # إنشاء نافذة متصفح احترافية
    # width/height: أبعاد النافذة
    # resizable: قابلة للتكبير
    window = webview.create_window(
        'AboElfadl Secure Viewer', 
        'https://google.com', 
        width=1000, 
        height=700,
        resizable=True,
        background_color='#1e1e1e' # لون الخلفية الداكن
    )
    
    # تشغيل النافذة
    webview.start()

if __name__ == '__main__':
    start_browser()