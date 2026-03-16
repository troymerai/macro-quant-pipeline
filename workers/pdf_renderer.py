import os
import markdown
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)

def render_markdown_to_pdf(markdown_text: str, output_filename="macro_report.pdf") -> str:
    """AI가 작성한 마크다운 텍스트를 HTML로 변환한 뒤 PDF로 렌더링합니다."""
    
    logger.info("🖨️ PDF 렌더링 엔진 가동 시작...")

    try:
        # 1. 마크다운을 HTML 태그로 변환
        html_content = markdown.markdown(markdown_text, extensions=['tables', 'fenced_code'])
        
        # 2. Jinja2 템플릿 환경 불러오기
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('report_base.html')
        
        # 3. 템플릿에 데이터(HTML 본문, 오늘 날짜) 매핑
        today_str = datetime.now().strftime("%Y년 %m월 %d일")
        rendered_html = template.render(content=html_content, date=today_str)
        
        # 4. 결과물을 저장할 reports 폴더 생성
        os.makedirs("reports", exist_ok=True)
        output_path = os.path.join("reports", output_filename)
        
        # 5. WeasyPrint를 이용해 PDF로 렌더링 및 저장
        HTML(string=rendered_html, base_url=os.path.abspath('templates')).write_pdf(
            output_path, 
            stylesheets=[CSS(filename='templates/style.css')]
        )
        
        logger.info(f"✅ PDF 리포트 생성 완료: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"❌ PDF 렌더링 중 에러 발생: {e}")
        raise e