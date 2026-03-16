import sys
import os
from core.notion_client import fetch_selected_from_notion, update_notion_checkbox
from core.gemini_client import generate_deep_research_report
from workers.pdf_renderer import render_markdown_to_pdf
from core.telegram_client import send_pdf_report, send_admin_message # 👈 관리자 알림 함수 추가

def main():
    try:
        # 1. 시작 알림 보고
        send_admin_message("⏳ <b>[Part B 시작]</b> 노션 데이터를 바탕으로 AI 딥리서치 및 리포트 생성을 시작합니다.\n<i>(PDF 렌더링 및 채널 배포 진행 중...)</i>")

        print("\n=== [1단계: 노션 클린 데이터 추출] ===")
        selected_data = fetch_selected_from_notion()
        
        if not selected_data:
            empty_msg = "⚠️ 채택된 데이터가 없어 리포트를 발행하지 않고 종료합니다."
            print(empty_msg)
            send_admin_message(empty_msg) # 데이터 없을 때도 보고
            sys.exit(0)

        print("\n=== [2단계: Gemini Deep Research 가동] ===")
        report_markdown = generate_deep_research_report(selected_data)
        
        print("\n=== [3단계: PDF 리포트 렌더링] ===")
        pdf_path = render_markdown_to_pdf(report_markdown)
        
        print("\n=== [4단계: 텔레그램 자동 배포] ===") 
        caption_msg = "📊 <b>오늘의 글로벌 매크로 심층 분석 리포트</b>\n\nAI 기반 팩트체크를 통과한 클린 데이터로 작성되었습니다. 첨부된 PDF를 확인해 주세요!"
        
        is_sent = send_pdf_report(pdf_path, caption_msg)
        
        if is_sent:
            print("✅ 텔레그램 채널 전송 성공!")
            print("\n=== [5단계: 사후 처리 및 스토리지 최적화] ===")
            
            print("🧹 사용된 노션 데이터의 '채택' 상태를 초기화합니다...")
            for data in selected_data:
                update_notion_checkbox(data["id"], property_name="채택", is_checked=False)
            print("✅ 노션 데이터 초기화 완료!")

            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"🗑️ 전송 완료된 임시 PDF 파일 삭제 완료: {pdf_path}")
            
            # 2. 성공 알림 보고
            send_admin_message("✅ <b>[Part B 완료]</b> 심층 리포트 생성 및 채널 배포가 성공적으로 완료되었습니다! 노션 체크박스도 초기화했습니다.")
                
        else:
            print("❌ 텔레그램 채널 전송 실패 (사후 처리를 진행하지 않습니다)")
            send_admin_message("❌ <b>[Part B 에러]</b> 리포트 생성은 성공했으나, 채널 배포(PDF 전송)에 실패했습니다.")
        
        print("\n===================================")
        print(f"🎉 [Part B 완료] 프로세스 종료!")

    except Exception as e:
        # 3. 치명적 에러 알림 보고
        error_msg = f"❌ <b>[Part B 치명적 에러]</b> 파이프라인이 중단되었습니다.\n에러 내용: {str(e)}"
        print(f"\n{error_msg}")
        send_admin_message(error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()