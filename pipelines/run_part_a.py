import sys
from core.telegram_client import send_admin_message
from workers.scraper import collect_all_data
from workers.fact_checker import run_fact_check
from core.notion_client import upload_to_notion

def main():
    try:
        # 1. 시작 알림 (인간 통제 구역 설정)
        send_admin_message("⏳ <b>[Part A 시작]</b> 매크로 데이터 수집 및 팩트체크를 시작합니다.\n⚠️ <i>작업이 끝날 때까지 노션을 건드리지 마세요!</i>")

        # 2. 데이터 크롤링
        print("\n=== [1단계: 데이터 수집] ===")
        raw_data = collect_all_data()
        if not raw_data:
            raise ValueError("수집된 데이터가 없습니다. data_sources.json 설정을 확인해주세요.")

        # 3. AI 팩트체크 팀장 가동
        print("\n=== [2단계: AI 팩트체크 및 오염도 계산] ===")
        verified_data = run_fact_check(raw_data)

        # 4. 노션 데이터베이스 적재
        print("\n=== [3단계: 노션 적재] ===")
        success_count = 0
        for data in verified_data:
            print(f"업로드 중: {data['name']} ...", end=" ")
            if upload_to_notion(data):
                print("✅ 성공")
                success_count += 1
            else:
                print("❌ 실패")
        
        # 5. 작업 완료 알림 (인간 큐레이션 요청)
        success_msg = f"✅ <b>[Part A 완료]</b> 총 {success_count}개의 검증된 데이터가 노션에 적재되었습니다!\n👉 지금 노션에 접속해서 오늘 리포트로 발행할 핵심 자료에 체크(✅)해 주세요."
        send_admin_message(success_msg)
        print(f"\n🎉 모든 과정이 끝났습니다. 텔레그램 알림을 확인하세요!")

    except Exception as e:
        # 치명적 에러 발생 시 텔레그램으로 즉시 보고 후 종료
        error_msg = f"❌ <b>[Part A 치명적 에러]</b> 파이프라인이 중단되었습니다.\n에러 내용: {str(e)}"
        send_admin_message(error_msg)
        print(f"\n{error_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()