import sys
import io
import time
import re
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_price(price_str):
    clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        digits_only = re.sub(r'[^0-9]', '', parts[1])
        man = int(digits_only) * 10000 if digits_only else 0
        return eok + man
    return 0

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()

        print("==================================================================")
        print("💡 기획자님 피드백 반영: 네이버 고유 '평형 드롭다운(ptpNo)' URL 직접 타격!")
        print("==================================================================")
        
        # 기획자님의 '30평' 드롭다운 메뉴는 네이버 내부적으로 ptpNo=1 로 지정됩니다.
        # 강제 spcMin 수학 필터를 버리고, 네이버 고유 평형 분리 인덱스(ptpNo=1)를 직접 URL에 박아 넣습니다.
        url = "https://new.land.naver.com/complexes/8928?a=APT&b=A1&ptpNo=1&prcSort=asc"
        
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector(".item_inner", timeout=10000)
        
        # 기획자님이 스크린샷에서 누르신 '동일매물 묶기'를 봇이 직접 마우스로 클릭하게 만듭니다.
        try:
            page.locator("label:has-text('동일매물 묶기')").click(timeout=3000)
            time.sleep(2)  # 묶인 결과를 서버에서 받아올 때까지 대기
            print("   ✅ UI 클릭 완료: [동일매물 묶기] 활성화 (중복 어그로 제거!)")
        except:
            pass

        cards = page.locator(".item_inner").all()[:3]
        
        print("\n   🔍 필터 적용 최상단 매물 스캔:")
        for idx, card in enumerate(cards):
            text = card.inner_text().replace('\n', ' | ')
            price_text = card.locator(".price").first.inner_text().strip()
            
            print(f"      [{idx+1}등 매물] 가격: {price_text} 👉 원문: {text[:80]}...")
            if idx == 0:
                print(f"      🎯 => 즉시 추출된 찐 1등 최저호가: {price_text}\n")
                
        browser.close()

if __name__ == "__main__":
    test()
