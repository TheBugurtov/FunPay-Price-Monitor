import asyncio
import time
from playwright.async_api import async_playwright
import logging

# Настройка логов
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def get_min_price():
    async with async_playwright() as p:
        # Запуск браузера
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        url = "https://funpay.com/chips/209/?server=12605&side=106"
        
        try:
            await page.goto(url, wait_until="networkidle")
            # Ждем появления карточек
            await page.wait_for_selector(".tc-item", timeout=15000)
            items = await page.query_selector_all('a.tc-item[data-server="12605"][data-side="106"]')
            
            prices = []
            for item in items:
                price_div = await item.query_selector('.tc-price div')
                if price_div:
                    text = await price_div.inner_text()
                    clean_text = text.replace('₽', '').replace(',', '.').strip()
                    try:
                        price_val = float(clean_text)
                        if 0.1 < price_val < 100:
                            prices.append(price_val)
                    except ValueError:
                        continue
            
            await browser.close()
            return min(prices) if prices else None
            
        except Exception as e:
            logging.error(f"Ошибка при получении цены: {e}")
            await browser.close()
            return None

if __name__ == "__main__":
    # Бесконечный цикл для работы в фоне
    while True:
        min_price = asyncio.run(get_min_price())
        
        if min_price:
            logging.info(f"Найдена минимальная цена: {min_price} ₽")
            # Запись цены в файл
            with open(r"D:\Funpay\price.txt", "w", encoding="utf-8") as f:
                f.write(str(min_price))
        else:
            logging.warning("Не удалось получить цену в этом цикле.")
        
        # Задержка 5 минут (300 секунд) перед следующим запуском
        time.sleep(300)