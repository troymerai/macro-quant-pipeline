import requests
from config.settings import get_env

# 환경 변수에서 토큰과 ID 불러오기
BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = get_env("TELEGRAM_ADMIN_CHAT_ID")
PUBLIC_CHANNEL_ID = get_env("TELEGRAM_PUBLIC_CHANNEL_ID")

def send_admin_message(text):
    """관리자(개인)에게 시스템 알림이나 경고를 보냅니다."""
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        print(f"[로컬 테스트/관리자 알림] {text}")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": ADMIN_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"관리자 메시지 전송 실패: {e}")

def send_public_message(text):
    """공식 채널에 텍스트 메시지를 보냅니다."""
    if not BOT_TOKEN or not PUBLIC_CHANNEL_ID:
        print(f"[로컬 테스트/공식 채널] {text}")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": PUBLIC_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

def send_public_document(file_path, caption=""):
    """공식 채널에 최종 완성된 PDF 리포트(문서)를 보냅니다."""
    if not BOT_TOKEN or not PUBLIC_CHANNEL_ID:
        print(f"[로컬 테스트/문서 전송] 파일: {file_path}, 캡션: {caption}")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, 'rb') as doc:
            files = {'document': doc}
            data = {'chat_id': PUBLIC_CHANNEL_ID, 'caption': caption, 'parse_mode': 'HTML'}
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            print("✅ 채널에 리포트 전송 완료!")
    except Exception as e:
        error_msg = f"❌ 리포트 전송 중 에러 발생: {e}"
        print(error_msg)
        send_admin_message(error_msg) # 에러가 나면 관리자에게 즉시 알림

# 테스트용 코드
if __name__ == "__main__":
    send_admin_message("⏳ <b>[테스트]</b> 시스템 기본 세팅이 정상적으로 완료되었습니다.")