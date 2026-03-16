import sys
from core.notion_client import fetch_selected_from_notion
from core.gemini_client import generate_deep_research_report

def main():
    try:
        print("\n=== [1단계: 노션 클린 데이터 추출] ===")
        # 1. 노션에서 '채택'된 데이터 가져오기
        selected_data = fetch_selected_from_notion()
        
        if not selected_data:
            print("⚠️ 채택된 데이터가 없습니다. 파이프라인을 종료합니다.")
            sys.exit(0)

        print("\n=== [2단계: Gemini Deep Research 가동] ===")
        # 2. 데이터를 AI에게 넘겨 심층 리포트 작성
        report_markdown = generate_deep_research_report(selected_data)
        
        print("\n=== [3단계: 생성된 리포트 프리뷰] ===\n")
        print(report_markdown)
        print("\n===================================\n")
        print("🎉 [Part B - Deep Research] 리포트 생성이 완료되었습니다!")

        # TODO: 다음 스텝에서 이 마크다운을 PDF로 렌더링하고 텔레그램으로 쏘는 로직 추가 예정

    except Exception as e:
        print(f"\n❌ [Part B 에러 발생]: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()