import sys
import io
import re
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def parse_price(price_str):
    clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        man = int(re.sub(r'[^0-9]', '', parts[1])) * 10000 if re.sub(r'[^0-9]', '', parts[1]) else 0
        return eok + man
    return 0

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page(user_agent="Mozilla/5.0")
        
        # 기획자님 논리 완벽 구현!
        # 대치은마(8928) + 아파트 매매(A1, APT) + 전용 76㎡ 공급면적 환산(spcMin 93 ~ spcMax 109) + 최저가(asc)
        url = "https://new.land.naver.com/complexes/8928?a=APT&b=A1&spcMin=93&spcMax=110&prcSort=asc"
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector(".item_inner", timeout=10000)
        
        cards = page.locator(".item_inner").all()[:5]
        
        for card in cards:
            text = card.inner_text()
            if "지분" in text or "경매" in text: continue
            
            price_text = card.locator(".price").first.inner_text().strip()
            price_num = parse_price(price_text)
            
            # 20억 이하 어그로만 살미짝 방어
            if price_num >= 2000000000:
                print(f"🔥 대치은마 76㎡(30평형) 완벽 추출 👉 {price_text}")
                break
                
        browser.close()

if __name__ == "__main__":
    test()
