import sys
import os
from core.notion_client import fetch_selected_from_notion
from core.gemini_client import generate_deep_research_report
from workers.pdf_renderer import render_markdown_to_pdf
from core.telegram_client import send_pdf_report  # 👈 [추가됨] 텔레그램 전송 함수 불러오기

def main():
    try:
        print("\n=== [1단계: 노션 클린 데이터 추출] ===")
        selected_data = fetch_selected_from_notion()
        
        if not selected_data:
            print("⚠️ 채택된 데이터가 없습니다. 파이프라인을 종료합니다.")
            sys.exit(0)

        print("\n=== [2단계: Gemini Deep Research 가동] ===")
        report_markdown = generate_deep_research_report(selected_data)
        
        print("\n=== [3단계: PDF 리포트 렌더링] ===")
        pdf_path = render_markdown_to_pdf(report_markdown)
        
        # 👇 [추가됨] 4단계: 만들어진 PDF를 텔레그램으로 발송하는 로직
        print("\n=== [4단계: 텔레그램 자동 배포] ===") 
        caption_msg = "📊 <b>오늘의 글로벌 매크로 심층 분석 리포트</b>\n\nAI 기반 팩트체크를 통과한 클린 데이터로 작성되었습니다. 첨부된 PDF를 확인해 주세요!"
        
        # 전송 성공 여부 체크
        is_sent = send_pdf_report(pdf_path, caption_msg)
        if is_sent:
            print("✅ 텔레그램 채널 전송 성공!")
        else:
            print("❌ 텔레그램 채널 전송 실패 (로그를 확인하세요)")
        
        print("\n===================================")
        print(f"🎉 [Part B 완료] 리포트가 성공적으로 발행 및 배포되었습니다!")
        print(f"👉 로컬 확인 경로: {os.path.abspath(pdf_path)}")

    except Exception as e:
        print(f"\n❌ [Part B 에러 발생]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()