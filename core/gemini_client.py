import google.generativeai as genai
import json
import logging
from config.settings import get_env

# 로깅 설정 (운영 환경을 위해 print 대신 logging 권장)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API 키 초기화
API_KEY = get_env("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    logger.error("⚠️ 경고: GEMINI_API_KEY가 환경변수(.env)에 설정되지 않았습니다. API 호출이 실패합니다.")

def ask_gemini_json(prompt: str, system_instruction: str = "너는 유능한 AI 어시스턴트야.") -> dict:
    """Gemini에게 질문하고 무조건 JSON 형태로만 답변을 받아오는 핵심 함수"""
    if not API_KEY:
        return {"error": "API Key Missing", "summary": "분석 실패", "pollution_score": 100, "discrepancy_flag": True}

    try:
        # 빠르고 가성비 좋은 flash 모델 (대량의 기사 팩트체크에 최적화)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", 
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content(prompt)
        
        # 모델이 반환한 텍스트를 파이썬 딕셔너리로 안전하게 변환
        return json.loads(response.text)
        
    except json.JSONDecodeError:
        logger.error("❌ Gemini 응답이 올바른 JSON 형식이 아닙니다.")
        return {"error": "JSON Parse Error", "summary": "분석 실패", "pollution_score": 100, "discrepancy_flag": True}
    except Exception as e:
        logger.error(f"❌ Gemini API 호출 에러: {e}")
        return {"error": str(e), "summary": "분석 실패", "pollution_score": 100, "discrepancy_flag": True}