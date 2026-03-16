import sys
import os
from core.notion_client import fetch_selected_from_notion, update_notion_checkbox # 👈 업데이트 함수 임포트
from core.gemini_client import generate_deep_research_report
from workers.pdf_renderer import render_markdown_to_pdf
from core.telegram_client import send_pdf_report

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
        
        print("\n=== [4단계: 텔레그램 자동 배포] ===") 
        caption_msg = "📊 <b>오늘의 글로벌 매크로 심층 분석 리포트</b>\n\nAI 기반 팩트체크를 통과한 클린 데이터로 작성되었습니다. 첨부된 PDF를 확인해 주세요!"
        
        is_sent = send_pdf_report(pdf_path, caption_msg)
        
        # 👇 [새로 추가된 핵심 로직: 5단계 사후 처리]
        if is_sent:
            print("✅ 텔레그램 채널 전송 성공!")
            
            print("\n=== [5단계: 사후 처리 및 스토리지 최적화] ===")
            
            # 1. 노션 체크박스 초기화 (내일 중복 발행 방지)
            print("🧹 사용된 노션 데이터의 '채택' 상태를 초기화합니다...")
            for data in selected_data:
                update_notion_checkbox(data["id"], property_name="채택", is_checked=False)
            print("✅ 노션 데이터 초기화 완료!")

            # 2. 로컬 PDF 파일 삭제 (스토리지 및 깃허브 액션 최적화)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"🗑️ 전송 완료된 임시 PDF 파일 삭제 완료: {pdf_path}")
                
        else:
            print("❌ 텔레그램 채널 전송 실패 (사후 처리를 진행하지 않습니다)")
        
        print("\n===================================")
        print(f"🎉 [Part B 완료] 리포트 배포 및 사후 처리가 모두 성공적으로 완료되었습니다!")

    except Exception as e:
        print(f"\n❌ [Part B 에러 발생]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()