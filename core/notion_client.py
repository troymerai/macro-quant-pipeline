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


def get_page_content(page_id):
    """특정 노션 페이지의 본문(Block Children) 텍스트를 모두 긁어옵니다."""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    try:
        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        blocks = res.json().get("results", [])
        
        content_text = ""
        for b in blocks:
            b_type = b.get("type")
            # 단락이나 제목 블록에서 텍스트만 추출
            if b_type in ["paragraph", "heading_2", "heading_3", "heading_1"]:
                rich_text = b.get(b_type, {}).get("rich_text", [])
                if rich_text:
                    content_text += rich_text[0].get("plain_text", "") + "\n"
        return content_text.strip()
    except Exception as e:
        print(f"⚠️ 페이지 본문 읽기 실패 ({page_id}): {e}")
        return ""


def fetch_selected_from_notion():
    """노션 DB에서 '채택' 체크박스가 True인 데이터만 필터링해서 가져옵니다."""
    print("🔍 노션에서 '채택(✅)'된 클린 데이터를 조회합니다...")
    
    if not NOTION_TOKEN or not DATABASE_ID:
        print("⚠️ 노션 토큰이나 DB ID가 설정되지 않았습니다.")
        return []

    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # '채택' 속성이 True인 것만 가져오라는 강력한 필터 쿼리
    payload = {
        "filter": {
            "property": "채택",
            "checkbox": {
                "equals": True
            }
        }
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])

        selected_data = []
        for page in results:
            props = page.get("properties", {})

            # 1. 제목 파싱 (노션 JSON 구조 대응)
            title_prop = props.get("제목", {}).get("title", [])
            title = title_prop[0].get("plain_text", "제목 없음") if title_prop else "제목 없음"

            # 2. URL 파싱
            page_url = props.get("URL", {}).get("url", "")
            
            # 3. 페이지 ID 추출 및 본문 텍스트 읽어오기 (Deep Research용 재료)
            page_id = page.get("id")
            page_content = get_page_content(page_id)

            selected_data.append({
                "title": title,
                "url": page_url,
                "content": page_content
            })

        print(f"✅ 총 {len(selected_data)}개의 채택된 데이터를 성공적으로 불러왔습니다!")
        return selected_data

    except Exception as e:
        print(f"❌ 노션 데이터 조회 실패: {e}")
        return []


# 단독 실행 시 파트 B 테스트용 코드
if __name__ == "__main__":
    # 실제로 본인의 노션에서 기사 1~2개에 '채택' 체크박스를 누르고 실행해보세요!
    data = fetch_selected_from_notion()
    for d in data:
        print(f"\n📌 제목: {d['title']}")
        print(f"🔗 링크: {d['url']}")
        print(f"📝 내용 미리보기: {d['content'][:50]}...")