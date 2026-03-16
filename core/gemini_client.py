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
    
def generate_deep_research_report(curated_data: list) -> str:
    """선택된 노션 데이터를 융합하여 심층 마크다운 리포트를 생성합니다."""
    if not API_KEY:
        return "⚠️ API 키가 없어 리포트를 생성할 수 없습니다."

    logger.info("🧠 Gemini Deep Research 가동 중... 심층 분석 리포트를 작성합니다.")

    # 1. 노션에서 가져온 데이터를 하나의 거대한 프롬프트 텍스트로 병합
    context_text = ""
    for i, data in enumerate(curated_data, 1):
        context_text += f"\n### [자료 {i}] {data['title']}\n"
        context_text += f"- 출처: {data['url']}\n"
        context_text += f"- 내용:\n{data['content']}\n"
        context_text += "-" * 40

    # 2. 수석 퀀트 애널리스트 페르소나 부여
    system_instruction = """
    너는 월스트리트의 수석 매크로 퀀트 애널리스트야.
    제공된 여러 개의 검증된 기사와 경제 지표(Hard/Soft Data)를 단순 요약하지 마.
    이 데이터들이 상호작용하여 주식, 채권, 외환 시장에 미치는 영향을 거시적인 관점에서 엮어내고, 
    논리적이고 심도 있는 시황 보고서를 '마크다운(Markdown)' 형식으로 작성해 줘.
    
    [보고서 필수 구성 요소]
    # 📊 오늘의 글로벌 매크로 심층 분석
    ## 1. 서론 (시장 핵심 요약)
    ## 2. 주요 지표 및 섹터별 심층 분석
    ## 3. 퀀트 애널리스트의 종합 투자 인사이트 (결론)
    """
    
    prompt = f"아래 제공된 [클린 데이터]를 바탕으로 심층 매크로 리포트를 작성해줘.\n\n[클린 데이터]\n{context_text}"
    
    try:
        # 텍스트 생성용이므로 JSON 강제 설정(generation_config)을 뺍니다.
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", 
            system_instruction=system_instruction
        )
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"❌ Deep Research 생성 에러: {e}")
        return f"리포트 생성 중 에러가 발생했습니다: {str(e)}"