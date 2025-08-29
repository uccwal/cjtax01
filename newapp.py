import requests
import pymysql
import json
from flask import Flask, jsonify, request
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class PolicyFundCollector:
    def __init__(self,
                 host="chunjitax.mysql.pythonanywhere-services.com",
                 user="chunjitax",
                 password="tax0820!!",
                 database="chunjitax$default",
                 github_json_url = "https://raw.githubusercontent.com/uccwal/cjtax0/refs/heads/main/data.json"):
                 #    host = "localhost",
                 #    user = "root",
                 #    password = "0000",
                 #    database = "policy_funds",
                 #    github_json_url = "https://raw.githubusercontent.com/uccwal/cjtax0/refs/heads/main/data.json"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.github_json_url = github_json_url


    # ---- PolicyFundCollector 클래스 내부에 메서드 추가 ----

    def update_fund(self, fund_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE policy_funds
                SET pblancNm=%s, jrsdInsttNm=%s, trgetNm=%s, bsnsSumryCn=%s, pblancUrl=%s
                WHERE id=%s
            ''', (
                data.get('pblancNm'),
                data.get('jrsdInsttNm'),
                data.get('trgetNm'),
                data.get('bsnsSumryCn'),
                data.get('pblancUrl'),
                fund_id
            ))
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def delete_fund(self, fund_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM policy_funds WHERE id=%s", (fund_id,))
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def add_fund(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO policy_funds (
                    pblancId, pblancNm, pblancUrl, jrsdInsttNm,
                    excInsttNm, bsnsSumryCn, creatPnttm,
                    reqstBeginEndDe, pldirSportRealmLclasCodeNm,
                    trgetNm, hashTags, inqireCo, totCnt
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
            ''', (
                data.get('pblancId'),
                data.get('pblancNm'),
                data.get('pblancUrl'),
                data.get('jrsdInsttNm'),
                data.get('excInsttNm'),
                data.get('bsnsSumryCn'),
                data.get('creatPnttm', datetime.now().strftime("%Y-%m-%d")),
                data.get('reqstBeginEndDe'),
                data.get('pldirSportRealmLclasCodeNm'),
                data.get('trgetNm'),
                data.get('hashTags'),
                data.get('inqireCo', 0),
                data.get('totCnt', 0)
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

# ---- Flask 라우트 추가 ----

@app.route('/manage/add', methods=['GET', 'POST'])
def add_fund():
    if request.method == 'POST':
        data = request.form.to_dict()
        new_id = collector.add_fund(data)
        return f"<p>추가 완료 (ID={new_id}) <a href='/manage'>돌아가기</a></p>"
    return '''
        <h2>새 정책자금 추가</h2>
        <form method="post">
            제목: <input type="text" name="pblancNm"><br>
            기관: <input type="text" name="jrsdInsttNm"><br>
            대상: <input type="text" name="trgetNm"><br>
            요약: <textarea name="bsnsSumryCn"></textarea><br>
            URL: <input type="text" name="pblancUrl"><br>
            <input type="submit" value="추가">
        </form>
    '''

@app.route('/manage/edit/<int:fund_id>', methods=['GET', 'POST'])
def edit_fund(fund_id):
    if request.method == 'POST':
        data = request.form.to_dict()
        updated = collector.update_fund(fund_id, data)
        return f"<p>{updated}건 수정 완료 <a href='/manage'>돌아가기</a></p>"

    # GET: 수정폼 표시
    conn = collector.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM policy_funds WHERE id=%s", (fund_id,))
    fund = cursor.fetchone()
    conn.close()
    if not fund:
        return "데이터 없음", 404

    return f'''
        <h2>정책자금 수정 (ID={fund_id})</h2>
        <form method="post">
            제목: <input type="text" name="pblancNm" value="{fund['pblancNm'] or ''}"><br>
            기관: <input type="text" name="jrsdInsttNm" value="{fund['jrsdInsttNm'] or ''}"><br>
            대상: <input type="text" name="trgetNm" value="{fund['trgetNm'] or ''}"><br>
            요약: <textarea name="bsnsSumryCn">{fund['bsnsSumryCn'] or ''}</textarea><br>
            URL: <input type="text" name="pblancUrl" value="{fund['pblancUrl'] or ''}"><br>
            <input type="submit" value="저장">
        </form>
    '''

@app.route('/manage/delete/<int:fund_id>', methods=['POST'])
def delete_fund(fund_id):
    deleted = collector.delete_fund(fund_id)
    return f"<p>{deleted}건 삭제 완료 <a href='/manage'>돌아가기</a></p>"


    def get_connection(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def init_database(self):
        # (기존 init_database 그대로 유지)
        pass

    def fetch_from_github(self):
        """GitHub Actions에서 생성된 data.json 가져오기"""
        try:
            logger.info(f"GitHub JSON 다운로드: {self.github_json_url}")
            response = requests.get(self.github_json_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info(f"총 {len(data)}개 데이터 로드")
            return data
        except Exception as e:
            logger.error(f"GitHub JSON 로드 실패: {e}")
            return []

    def save_to_database(self, items):
        # (기존 save_to_database 그대로 사용)
        conn = self.get_connection()
        cursor = conn.cursor()

        saved_count = 0
        for item in items:
            try:
                cursor.execute('''
                INSERT IGNORE INTO policy_funds (
                    pblancId, pblancNm, pblancUrl, jrsdInsttNm, excInsttNm,
                    bsnsSumryCn, creatPnttm, reqstBeginEndDe, pldirSportRealmLclasCodeNm,
                    trgetNm, hashTags, inqireCo, totCnt
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                )
                ''', (
                    item.get('pblancId'),
                    item.get('pblancNm'),
                    item.get('pblancUrl'),
                    item.get('jrsdInsttNm'),
                    item.get('excInsttNm'),
                    item.get('bsnsSumryCn'),
                    item.get('creatPnttm'),
                    item.get('reqstBeginEndDe'),
                    item.get('pldirSportRealmLclasCodeNm'),
                    item.get('trgetNm'),
                    item.get('hashTags'),
                    item.get('inqireCo', 0),
                    item.get('totCnt', 0)
                ))
                if cursor.rowcount > 0:
                    saved_count += 1
            except Exception as e:
                logger.error(f"DB 저장 오류: {e}")

        conn.commit()
        conn.close()
        logger.info(f"{saved_count}개 데이터 DB 저장 완료")
        return saved_count

    def update_from_github(self):
        """GitHub JSON → DB 저장"""
        data = self.fetch_from_github()
        if not data:
            return {"success": False, "message": "GitHub에서 데이터를 가져오지 못했습니다."}
        saved = self.save_to_database(data)
        return {"success": True, "saved_count": saved, "total_count": len(data)}

collector = PolicyFundCollector()

@app.route('/update_from_github')
def update_from_github():
    """GitHub JSON에서 DB 업데이트"""
    result = collector.update_from_github()
    return jsonify(result)

# 기존 /stats, /search, /manage 등은 그대로 사용 가능



@app.route('/stats')
def get_stats():
    try:
        stats = collector.get_database_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/search')
def search_funds():
    try:
        keyword = request.args.get('keyword', '')
        institution = request.args.get('institution', '')
        limit = request.args.get('limit', 20, type=int)

        if not keyword:
            return jsonify([])

        results = collector.search_funds(
            keyword=keyword,
            institution=institution if institution else None,
            limit=limit
        )
        return jsonify(results)
    except Exception as e:
        logger.error(f"검색 오류: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/manage')
def manage_page():
    try:
        page = request.args.get('page', 1, type=int)
        data = collector.get_funds_paginated(page=page, per_page=20)

        # 테이블 행들 생성
        table_rows = ""
        for item in data['items']:
            title = (item['pblancNm'] or '')[:50]
            table_rows += f"""
            <tr>
                <td>{item['id']}</td>
                <td>{title}</td>
                <td>{item['jrsdInsttNm'] or ''}</td>
                <td>{item['trgetNm'] or ''}</td>
                <td>{item['creatPnttm'] or ''}</td>
                <td>{item['inqireCo'] or 0}</td>
            </tr>"""

        # 페이지네이션
        pagination = ""
        if data['page'] > 1:
            pagination += f'<a href="/manage?page={data["page"] - 1}" class="btn">이전</a>'

        for p in range(max(1, data['page'] - 2), min(data['total_pages'] + 1, data['page'] + 3)):
            if p == data['page']:
                pagination += f'<span class="btn" style="background:#6c757d;">{p}</span>'
            else:
                pagination += f'<a href="/manage?page={p}" class="btn">{p}</a>'

        if data['page'] < data['total_pages']:
            pagination += f'<a href="/manage?page={data["page"] + 1}" class="btn">다음</a>'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>정책자금 관리</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .btn {{
            display: inline-block; padding: 8px 16px;
            background: #007bff; color: white; text-decoration: none;
            border-radius: 4px; margin: 2px;
        }}
        .btn:hover {{ background: #0056b3; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table th, .table td {{ padding: 8px; border: 1px solid #ddd; text-align: left; }}
        .table th {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>정책자금 관리</h1>
        <p><a href="/" class="btn">메인으로</a></p>

        <p>총 {data['total']}건 | {data['page']}/{data['total_pages']} 페이지</p>

        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>제목</th>
                    <th>기관</th>
                    <th>대상</th>
                    <th>등록일</th>
                    <th>조회수</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>

        <div style="text-align: center;">
            {pagination}
        </div>
    </div>
</body>
</html>"""

        return html
    except Exception as e:
        return f"오류: {str(e)}"


@app.route('/debug')
def debug_api():
    try:
        result = collector.fetch_page_data(1)
        if result:
            return jsonify({
                'success': True,
                'url': result['url'],
                'response_keys': list(result['data'].keys()),
                'full_response': result['data'],
                'raw_response_preview': result['raw_response'][:2000]
            })
        else:
            return jsonify({
                'success': False,
                'error': 'API 호출 실패'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == "__main__":
    try:
        print("정책자금 수집기 서버 시작")
        print("http://localhost:5000 에서 접속하세요")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"서버 시작 오류: {e}")
        print("MySQL 서버가 실행 중인지 확인해주세요.")