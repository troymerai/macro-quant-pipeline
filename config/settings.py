import os
import json
from pathlib import Path
from dotenv import load_dotenv

# 현재 스크립트 파일의 절대 경로를 기준으로 루트 디렉토리 설정 (상대 경로의 핵심)
BASE_DIR = Path(__file__).resolve().parent.parent

# 로컬 환경을 위한 .env 로드 (GitHub Actions 환경에서는 자동으로 무시되고 Secrets를 씀)
load_dotenv(os.path.join(BASE_DIR, ".env"))

def get_env(key, default=None):
    """환경 변수를 안전하게 가져오는 함수"""
    return os.getenv(key, default)

def load_data_sources():
    """data_sources.json 파일을 읽어서 딕셔너리로 반환하는 함수"""
    json_path = os.path.join(BASE_DIR, "data_sources.json")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("sources", [])
    except FileNotFoundError:
        print(f"❌ 설정 파일을 찾을 수 없습니다: {json_path}")
        return []

# 테스트용 코드 (이 파일을 직접 실행했을 때만 작동)
if __name__ == "__main__":
    sources = load_data_sources()
    print(f"총 {len(sources)}개의 데이터 출처가 로드되었습니다.")
    for src in sources:
        print(f"- [{src['type'].upper()}] {src['name']} (신뢰도: {src['trust_level']})")