import google.generativeai as genai
import json
import logging
from config.settings import get_env
import time

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
    
# def generate_deep_research_report(curated_data: list) -> str:
#     """선택된 노션 데이터를 융합하여 심층 마크다운 리포트를 생성합니다."""
#     if not API_KEY:
#         return "⚠️ API 키가 없어 리포트를 생성할 수 없습니다."

#     logger.info("🧠 Gemini Deep Research 가동 중... 심층 분석 리포트를 작성합니다.")

#     # 1. 노션에서 가져온 데이터를 하나의 거대한 프롬프트 텍스트로 병합 (토큰 다이어트 적용)
#     context_text = ""
#     for i, data in enumerate(curated_data, 1):
#         # 텍스트가 너무 길면 API 한도에 걸리므로, 각 기사당 최대 1500자로 자릅니다.
#         safe_content = data['content'][:1500] 
        
#         context_text += f"\n### [자료 {i}] {data['title']}\n"
#         context_text += f"- 출처: {data['url']}\n"
#         context_text += f"- 내용:\n{safe_content}...\n"
#         context_text += "-" * 40

#     system_instruction = """
#     너는 월스트리트의 수석 매크로 퀀트 애널리스트야.
#     제공된 여러 개의 검증된 기사와 경제 지표(Hard/Soft Data)를 단순 요약하지 마.
#     이 데이터들이 상호작용하여 주식, 채권, 외환 시장에 미치는 영향을 거시적인 관점에서 엮어내고, 
#     논리적이고 심도 있는 시황 보고서를 '마크다운(Markdown)' 형식으로 작성해 줘.
    
#     [보고서 필수 구성 요소]
#     # 📊 오늘의 글로벌 매크로 심층 분석
#     ## 1. 서론 (시장 핵심 요약)
#     ## 2. 주요 지표 및 섹터별 심층 분석
#     ## 3. 퀀트 애널리스트의 종합 투자 인사이트 (결론)
#     """
    
#     prompt = f"아래 제공된 [클린 데이터]를 바탕으로 심층 매크로 리포트를 작성해줘.\n\n[클린 데이터]\n{context_text}"
    
#     max_retries = 3  # 최대 3번까지 재시도
#     for attempt in range(max_retries):
#         try:
#             model = genai.GenerativeModel(
#                 model_name="gemini-2.0-flash", 
#                 system_instruction=system_instruction
#             )
#             response = model.generate_content(prompt)
#             return response.text
            
#         except Exception as e:
#             error_msg = str(e)
#             # 429 에러(한도 초과)인 경우 60초 대기 후 재시도
#             if "429" in error_msg or "Quota" in error_msg:
#                 if attempt < max_retries - 1:
#                     logger.warning(f"⏳ API 한도 초과(429). 60초 대기 후 재시도합니다... (시도 {attempt + 1}/{max_retries})")
#                     time.sleep(60)
#                 else:
#                     logger.error("❌ 최대 재시도 횟수를 초과했습니다.")
#                     return f"리포트 생성 실패 (API 한도 초과): {error_msg}"
#             else:
#                 # 429가 아닌 다른 치명적인 에러일 경우 즉시 중단
#                 logger.error(f"❌ Deep Research 생성 에러: {e}")
#                 return f"리포트 생성 중 에러가 발생했습니다: {error_msg}"

def generate_deep_research_report(curated_data: list) -> str:
    """선택된 노션 데이터를 융합하여 심층 마크다운 리포트를 생성합니다."""
    logger.info("🧠 [TEST MODE] Gemini API 한도 제한 우회를 위해 Mock 데이터를 반환합니다.")
    
    # 실제 운영 시에는 이 아래에 있는 주석 처리된 코드를 다시 살리면 됩니다.
    mock_markdown_report = """
# 📊 오늘의 글로벌 매크로 심층 분석 리포트

## 1. 서론 (시장 핵심 요약)
현재 글로벌 매크로 시장은 인플레이션 둔화와 미 연준(Fed)의 금리 인하 기대감이 교차하며 변동성이 확대되고 있습니다. 노션에서 큐레이션된 최상위 지표들을 분석한 결과, 실물 경제의 연착륙(Soft Landing) 가능성이 여전히 높게 평가되고 있습니다.

## 2. 주요 지표 및 섹터별 심층 분석
* **채권 시장 (Hard Data 분석)**
  * 국채 금리는 하향 안정화 추세를 보이고 있으며, 이는 기술주 및 성장주의 밸류에이션 부담을 낮추는 핵심 요인으로 작용하고 있습니다.
* **주식 시장 (Soft Data 교차 검증)**
  * S&P 500은 펀더멘털의 지지를 받으며 강세를 유지 중입니다. AI가 팩트체크한 뉴스들에 따르면 과도한 공포를 조장하는 노이즈는 시장에 큰 영향을 미치지 못하고 있습니다.

## 3. 퀀트 애널리스트의 종합 투자 인사이트 (결론)
현재 시점에서는 우량한 현금 흐름을 창출하는 **퀄리티 주식(Quality Stocks)**과 **중장기 국채**를 결합하는 바벨 전략(Barbell Strategy)이 가장 유효할 것으로 판단됩니다.
    """
    
    return mock_markdown_report.strip()

    """
    =========================================
    [아래는 실제 API 호출 코드입니다. 내일 API 한도가 풀리면 위 return문을 지우고 아래 주석을 해제하세요]
    
    # 1. 노션에서 가져온 데이터를 하나의 거대한 프롬프트 텍스트로 병합
    context_text = ""
    for i, data in enumerate(curated_data, 1):
        safe_content = data['content'][:1500] 
        context_text += f"\\n### [자료 {i}] {data['title']}\\n"
        context_text += f"- 출처: {data['url']}\\n"
        context_text += f"- 내용:\\n{safe_content}...\\n"
        context_text += "-" * 40

    system_instruction = "너는 월스트리트의 수석 매크로 퀀트 애널리스트야. (중략)"
    prompt = f"아래 제공된 [클린 데이터]를 바탕으로 심층 매크로 리포트를 작성해줘.\\n\\n[클린 데이터]\\n{context_text}"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel(model_name="gemini-2.0-flash", system_instruction=system_instruction)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # 에러 처리 로직...
            pass
    return "생성 실패"
    =========================================
    """