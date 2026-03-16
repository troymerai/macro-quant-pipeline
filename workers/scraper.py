import requests
from bs4 import BeautifulSoup
from config.settings import load_data_sources

def get_text_from_web(url):
    """일반 웹페이지/뉴스 기사에서 텍스트를 추출하는 함수"""
    try:
        # 웹사이트가 크롤링 봇을 차단하지 못하도록 일반 브라우저인 것처럼 위장
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 접속 실패 시 에러 발생
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 본문 텍스트가 있을 만한 <p> 태그를 모두 찾아서 이어붙임
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # 텍스트가 너무 길면 AI 분석 시 토큰(비용)이 낭비되므로 적절히 자름
        return text[:3000] if text else "본문 텍스트를 찾을 수 없습니다."
        
    except Exception as e:
        return f"크롤링 에러 발생: {e}"

def collect_all_data():
    """data_sources.json의 모든 출처를 순회하며 데이터를 수집"""
    sources = load_data_sources()
    collected_data = []

    print("🔍 데이터 수집을 시작합니다...")
    
    for source in sources:
        print(f"➡️ 수집 중: [{source['type'].upper()}] {source['name']}")
        
        raw_content = ""
        
        if source['method'] == 'api':
            # FRED 등 정형 데이터 API 호출 로직 (현재는 임시 텍스트)
            # 향후 FRED API 키를 연동해 실제 지표 값을 가져오도록 확장할 부분입니다.
            raw_content = f"{source['name']} 데이터 API 호출 성공 (수치 데이터 연동 예정)"
            
        elif source['method'] == 'scraping':
            # 뉴스, 블로그, 유튜브 텍스트 등 비정형 데이터 크롤링
            raw_content = get_text_from_web(source['url'])
            
        collected_data.append({
            "id": source['id'],
            "name": source['name'],
            "category": source['category'],
            "type": source['type'], # hard_data 또는 soft_data
            "trust_level": source['trust_level'], # AI 팩트체크 시 가중치로 사용됨
            "url": source['url'],
            "raw_content": raw_content
        })
        
    print(f"✅ 총 {len(collected_data)}개의 데이터 출처 수집 완료!")
    return collected_data

# 단독 실행 시 테스트용 코드
if __name__ == "__main__":
    data = collect_all_data()
    print("\n--- 수집 결과 요약 ---")
    for d in data:
        print(f"[{d['trust_level']}점] {d['name']}: 본문 길이 {len(d['raw_content'])}자")