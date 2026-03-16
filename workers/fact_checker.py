from core.gemini_client import ask_gemini_json
import logging

logger = logging.getLogger(__name__)

def run_fact_check(collected_data: list) -> list:
    """수집된 데이터를 Hard Data와 Soft Data로 나누어 팩트체크를 진행합니다."""
    print("🕵️‍♂️ AI 팩트체크 팀장이 검증을 시작합니다...")
    
    hard_data_list = [d for d in collected_data if d.get('type') == 'hard_data']
    soft_data_list = [d for d in collected_data if d.get('type') == 'soft_data']
    
    # Hard Data 컨텍스트 빌드
    hard_context = "\n".join([f"- {d.get('name', '알수없음')}: {d.get('raw_content', '')}" for d in hard_data_list])
    if not hard_context.strip():
        hard_context = "현재 수집된 Hard Data 기준점이 없습니다. (팩트체크 기준 없음)"

    verified_results = []
    
    system_prompt = """
    너는 월스트리트 최고 수준의 매크로 퀀트 펀드 '팩트체크 팀장'이야.
    주어진 뉴스나 오피니언(Soft Data)을 실제 경제 지표(Hard Data)와 비교 분석해야 해.
    
    반드시 아래 JSON 형식으로만 답변해:
    {
      "summary": "기사의 핵심 요약 (3문장 이내)",
      "discrepancy_flag": true/false (실제 지표와 방향성이 반대이거나 과장되었으면 true),
      "pollution_score": 0~100 (조회수 장사, 자극적 표현, 논리 비약이 심할수록 높은 점수),
      "reason": "왜 이런 오염도와 괴리율을 평가했는지 1문장으로 설명"
    }
    """

    for data in soft_data_list:
        data_name = data.get('name', '제목 없음')
        print(f"  ▶️ 검증 중: {data_name}")
        
        user_prompt = f"""
        [기준 지표 (Hard Data)]
        {hard_context}
        
        [검증할 대상 (Soft Data)]
        - 출처명: {data_name}
        - 내용: {data.get('raw_content', '')}
        
        위 대상을 분석해서 JSON으로 결과를 도출해줘.
        """
        
        # Gemini API 호출
        ai_result = ask_gemini_json(prompt=user_prompt, system_instruction=system_prompt)
        
        # 결과 매핑 및 방어적 데이터 처리
        data['ai_summary'] = ai_result.get('summary', '요약 실패')
        # 불리언 값이 아닐 수 있는 예외 상황 대비 강제 형변환
        data['discrepancy_flag'] = bool(ai_result.get('discrepancy_flag', True))
        data['ai_reason'] = ai_result.get('reason', '분석 사유 누락됨')
        
        # 오염도 및 페널티 계산 로직 (수학 연산 시 타입 에러 방지)
        try:
            base_pollution = float(ai_result.get('pollution_score', 50))
            trust_level = float(data.get('trust_level', 50))
            trust_penalty = (100 - trust_level) * 0.2
            
            # 최종 점수는 0~100 사이로 클리핑
            final_score = int(max(0, min(100, base_pollution + trust_penalty)))
            data['pollution_score'] = final_score
        except (ValueError, TypeError):
            logger.warning(f"[{data_name}] 오염도 계산 중 오류 발생. 기본값 100을 부여합니다.")
            data['pollution_score'] = 100
        
        verified_results.append(data)
        
    print(f"✅ 총 {len(verified_results)}개의 Soft Data 팩트체크 완료!")
    
    # 최종적으로 Hard Data와 검증이 완료된 Soft Data를 합쳐서 반환
    return hard_data_list + verified_results