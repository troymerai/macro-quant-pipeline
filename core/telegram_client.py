import requests
from config.settings import get_env

def send_telegram_message(chat_id_key, message):
    """지정한 환경변수 키(관리자/공개채널)를 기반으로 메시지를 보냅니다."""
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env(chat_id_key)
    
    if not token or not chat_id:
        print(f"⚠️ 텔레그램 설정이 누락되었습니다: {chat_id_key}")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 텔레그램 메시지 전송 실패: {e}")
        return False

def send_pdf_report(pdf_path, caption):
    """최종 PDF를 공개 채널로 배포합니다."""
    token = get_env("TELEGRAM_BOT_TOKEN")
    # 리포트는 공개 채널 ID로 전송
    chat_id = get_env("TELEGRAM_PUBLIC_CHANNEL_ID")
    
    if not token or not chat_id:
        print("⚠️ 텔레그램 공개 채널 ID 설정이 누락되었습니다.")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    
    try:
        with open(pdf_path, 'rb') as doc:
            files = {'document': doc}
            data = {
                'chat_id': chat_id,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            res = requests.post(url, data=data, files=files)
            res.raise_for_status()
        print("✈️ 텔레그램 채널로 리포트 배포 완료!")
        return True
    except Exception as e:
        print(f"❌ 텔레그램 PDF 배포 실패: {e}")
        return False

# 기존에 쓰던 함수를 래핑하여 호환성 유지
def send_admin_message(message):
    return send_telegram_message("TELEGRAM_ADMIN_CHAT_ID", message)