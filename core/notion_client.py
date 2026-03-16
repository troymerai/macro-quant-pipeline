import requests
from config.settings import get_env

NOTION_TOKEN = get_env("NOTION_TOKEN")
DATABASE_ID = get_env("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def upload_to_notion(data):
    """팩트체크가 완료된 딕셔너리 데이터를 노션 DB의 새 행(Page)으로 추가합니다."""
    
    if not NOTION_TOKEN or not DATABASE_ID:
        print("⚠️ 노션 토큰이나 DB ID가 설정되지 않았습니다.")
        return False

    url = "https://api.notion.com/v1/pages"

    # 노션 DB 속성(Property) 매핑 구조체
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "제목": {
                "title": [{"text": {"content": data.get("name", "제목 없음")}}]
            },
            "유형": {
                "select": {"name": data.get("type", "unknown")}
            },
            "카테고리": {
                "select": {"name": data.get("category", "unknown")}
            },
            "오염도": {
                "number": data.get("pollution_score", 0)
            },
            "괴리경고": {
                "checkbox": data.get("discrepancy_flag", False)
            },
            "채택": {
                "checkbox": False # 초기값은 무조건 False (우리가 나중에 수동 체크)
            }
        },
        # 페이지 본문(내부)에 들어갈 상세 내용 (마크다운 형식)
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "🤖 AI 팩트체크 요약"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": data.get("ai_summary", "요약 없음")}}]}
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"text": {"content": "💡 AI 판단 사유"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": data.get("ai_reason", "-")}}]}
            }
        ]
    }
    
    # URL 데이터가 있을 때만 속성에 추가 (빈 문자열이면 노션 API가 에러를 뱉음)
    if data.get("url"):
        payload["properties"]["URL"] = {"url": data["url"]}

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"❌ 노션 업로드 실패 [{data.get('name')}]: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ 네트워크/기타 에러: {e}")
        return False

# 단독 실행 시 테스트용 코드
if __name__ == "__main__":
    dummy_result = {
        "name": "[테스트] 연준 금리 인상 쇼크?",
        "type": "soft_data",
        "category": "market_news",
        "pollution_score": 85,
        "discrepancy_flag": True,
        "url": "https://example.com",
        "ai_summary": "유튜버가 연준이 내일 10% 금리 인상을 할 것이라고 자극적으로 주장함.",
        "ai_reason": "실제 FRED 지표의 방향성과 완전히 다르며 공포심을 조장하는 조회수 목적의 콘텐츠로 판단됨."
    }
    
    success = upload_to_notion(dummy_result)
    if success:
        print("✅ 노션 데이터베이스를 확인해 보세요! 페이지가 예쁘게 생성되었을 겁니다.")