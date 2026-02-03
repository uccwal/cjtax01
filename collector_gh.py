import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"
CERT_KEY = "86r0Kl"
PAGE_SIZE = 100  # 한 페이지당 가져올 개수

OUTPUT_FILENAME = "data.json"


def fetch_page(page_index=1):
    params = {
        'crtfcKey': CERT_KEY,
        'dataType': 'json',
        'pageIndex': page_index,
        'pageUnit': PAGE_SIZE,  # 추가
        'searchLclasId': '01',
        'hashtags': '금융,서울,부산,대구,인천,광주,대전,경기,강원,충북,충남,전북,전남,경북,경남',
        'searchCnt': PAGE_SIZE
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        logger.info(f"페이지 {page_index} 상태: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        items = data.get('jsonArray', [])
        logger.info(f"페이지 {page_index}: {len(items)}개 수집")
        return items
    except Exception as e:
        logger.error(f"페이지 {page_index} 오류: {e}")
        return []


def collect_all():
    all_items = []
    page_index = 1

    logger.info("=== 데이터 수집 시작 ===")

    while True:
        items = fetch_page(page_index)

        # 0개 나오면 중단
        if not items or len(items) == 0:
            logger.info(f"페이지 {page_index}에서 0개 반환 → 수집 종료")
            break

        all_items.extend(items)
        logger.info(f"현재까지 총 {len(all_items)}개 수집")

        page_index += 1

        # 무한루프 방지 (옵션)
        if page_index > 10000:
            logger.warning("10000페이지 초과, 안전 중단")
            break

    logger.info(f"=== 수집 완료: 총 {len(all_items)}개 ===")
    return all_items


def save_json(data):
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"파일 저장 완료 → {OUTPUT_FILENAME}")


if __name__ == "__main__":
    data = collect_all()
    if data:
        save_json(data)
    else:
        logger.error("수집된 데이터가 없습니다.")
