# 📊 AI Macro Quant Pipeline

AI(Gemini)와 Notion, Telegram을 활용하여 매일 글로벌 거시경제(Macro) 데이터를 수집, 팩트체크, 분석하고 최종 PDF 리포트로 자동 배포하는 서버리스(Serverless) 파이프라인입니다. 무분별한 AI 생성 가짜 뉴스를 필터링하고 인간의 큐레이션을 결합한 **Human-in-the-Loop** 아키텍처를 특징으로 합니다.

## ⏱️ Pipeline Scenario (Daily Schedule)

* **07:00 [Part A 시작]** GitHub Actions 스케줄러 가동. 관리자 텔레그램 봇으로 시작 알림 전송. 파이썬이 `data_sources.json`을 기반으로 시장 데이터 수집 시작.
* **07:05 [AI 팩트체크]** AI 팀장 에이전트가 뉴스/칼럼(Soft Data)을 실제 경제 지표(Hard Data)와 대조. 지표 괴리율 및 AI 무단 재생산(오염 데이터) 확률을 수치화.
* **07:10 [Part A 완료]** 1차 요약 및 팩트체크 스코어가 Notion DB에 적재 완료. 관리자 봇으로 큐레이션 요청 알림 전송.
* **12:00 [Human Curation]** 사용자가 스마트폰으로 Notion 접속. 'AI 오염 확률'과 '경고(Red Flag)' 태그를 참고하여 가장 신뢰도 높은 클린 데이터 10개 채택(✅).
* **15:00 [Part B 시작]** 스케줄러 가동. 채택된 10개의 클린 데이터만 추출하여 Gemini Deep Research 가동.
* **15:05 [리포트 창작]** Gemini가 데이터를 융합하여 월스트리트 퀀트 애널리스트 수준의 심층 시황 보고서(Markdown) 작성.
* **15:10 [Part B 완료]** 작성된 텍스트를 A4 사이즈 PDF로 렌더링. SNS 자동 포스팅 및 텔레그램 공식 채널로 PDF 최종 배포 완료.

---

## ⚙️ System Architecture & Process

### 0. Infrastructure
* **Config-Driven:** `data_sources.json`에 출처별 신뢰도(Trust Level) 가중치를 부여하여 코드 수정 없이 데이터 소스 관리.
* **Security:** API Key 등 민감 정보는 `.env` 및 GitHub Secrets로 완전 분리.
* **Two-Track Alert:** 시스템 에러/경고용 관리자 '개인 봇'과 최종 리포트 배포용 '퍼블릭 채널' 분리 운영.

### 1. Part A: Data Collection & Fact-Check
* **데이터 계층 분리:** 절대적 사실(Hard Data)과 오염 가능성이 있는 뉴스(Soft Data)를 구조적으로 분리 수집.
* **AI Fact-Checker:** * *Divergence Check:* 뉴스 주장이 실제 지표와 모순될 경우 ⚠️ 경고 태그 부여.
  * *AIGC Detection:* 텍스트가 AI 모델 붕괴로 재생산된 무의미한 데이터일 확률(0~100%) 계산.
* **Notion 적재:** 요약 텍스트와 함께 `AI Probability`, `Fact-Check Alert`, `Source Trust` 메타데이터 태깅.

### 2. Human-in-the-Loop
* 인간은 단순 요약이 아닌, AI가 미리 계산해 둔 '위험도 지표'를 바탕으로 직관적이고 빠른 최종 의사결정(체크박스 선택)만 수행.

### 3. Part B: Deep Research & Publishing
* **Trader Agent:** 필터링된 10개의 클린 데이터를 Gemini에 주입하여 단순 요약이 아닌 시장 상호작용 및 거시적 인사이트 중심의 리포트 생성 (서론, 섹터 분석, 결론).
* **PDF Rendering:** Jinja2와 WeasyPrint를 활용해 Markdown을 디자인된 HTML/CSS 템플릿에 매핑하여 즉시 PDF로 변환.
* **Auto Distribution:** Playwright 활용 블로그 자동 포스팅 및 Telegram API를 통한 채널 직배송.

---

## 📂 Directory Structure

```text
macro-quant-pipeline/
│
├── .env                    # (보안) API 키, 토큰 등 민감한 환경변수 보관 (Git 업로드 금지)
├── .gitignore              # (설정) Git 버전 관리에서 제외할 파일/폴더 목록 (reports/, .env 등)
├── data_sources.json       # (설정) 크롤링 대상 URL, API 및 매체별 신뢰도(Trust Level) 관리
├── requirements.txt        # (패키지) 파이프라인 구동에 필요한 파이썬 라이브러리 목록
│
├── .github/                # [인프라 계층] GitHub Actions CI/CD 스케줄러 (무인 자동화)
│   └── workflows/
│       ├── part_a_morning.yml     # 오전 7시: 데이터 수집 및 팩트체크 자동 실행 스크립트
│       └── part_b_afternoon.yml   # 오후 3시: 딥리서치 리포트 생성 및 배포 자동 실행 스크립트
│
├── config/                 # [설정 계층] 프로젝트 전역 설정 관리
│   ├── __init__.py
│   └── settings.py         # .env 파일을 읽어와 파이썬 전역에서 사용할 수 있게 해주는 로직
│
├── core/                   # [통신 계층] 외부 서비스(API)와의 통신 담당 (가장 안 변하는 뼈대)
│   ├── __init__.py
│   ├── gemini_client.py    # AI 두뇌: Gemini 2.0 Flash API 호출 (JSON 팩트체크, Markdown 리포트 작성)
│   ├── notion_client.py    # DB 관리: Notion API 연동 (데이터 적재, 채택된 데이터 추출, 상태 초기화)
│   └── telegram_client.py  # 알림망: Telegram Bot API 연동 (관리자 진행상황 보고, 채널 PDF 배포)
│
├── workers/                # [도메인 계층] 개별 단위 작업을 수행하는 실무자들 (핵심 비즈니스 로직)
│   ├── __init__.py
│   ├── fact_checker.py     # 검증 로직: AI 오염도 계산, 신뢰도 페널티 적용, 괴리율(Discrepancy) 판단
│   ├── pdf_renderer.py     # 렌더링 엔진: Markdown 텍스트를 HTML로 변환 후 WeasyPrint로 PDF 생성
│   └── scraper.py          # 수집기: BeautifulSoup을 이용한 웹 크롤링 및 API 데이터 수집
│
├── pipelines/              # [오케스트레이션] 워커(workers)와 코어(core)를 조립해 프로세스를 지휘하는 공장장
│   ├── __init__.py
│   ├── run_part_a.py       # Part A 메인 스위치: 크롤링 ➡️ 팩트체크 ➡️ 노션 DB 업로드 ➡️ 알림
│   └── run_part_b.py       # Part B 메인 스위치: 노션 추출 ➡️ 심층 리포트 생성 ➡️ PDF 변환 ➡️ 텔레그램 배포 ➡️ 노션 정리
│
├── templates/              # [프레젠테이션 계층] PDF 결과물 디자인 템플릿
│   ├── report_base.html    # Jinja2 문법이 적용된 리포트 HTML 뼈대
│   └── style.css           # 증권사 리포트 스타일의 CSS 디자인 (구글 웹폰트 적용)
│
└── reports/                # [출력물] Part B 실행 시 생성되는 최종 PDF 리포트 임시 저장소 (Git 제외)