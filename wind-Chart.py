import configparser
import os
import sys
import json
import mysql.connector
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re

# ===== 設定 Logging =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ===== 讀取 config.conf =====
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.conf')
config.read(config_path)

# ===== 資料庫參數 =====
DB_HOST = config['database']['host']
DB_USER = config['database']['user']
DB_PASSWORD = config['database']['password']
DB_NAME = config['database']['name']

# 設定 Firefox 選項 ===== Selenium 設定 =====
firefox_options = Options()
firefox_options.add_argument("--headless")  # 無頭模式
firefox_options.binary_location = config['paths']['firefox_binary']  # ← 加上這行，明確指定 Firefox 的執行檔

# 設定 Firefox Profile（優化載入）
firefox_options.set_preference("permissions.default.image", 2) # 不載入圖片
firefox_options.set_preference("browser.display.use_document_colors", False) # 停用顏色
firefox_options.set_preference("browser.display.use_document_fonts", 0) # 停用字型
firefox_options.set_preference("javascript.enabled", True) # 保留 JS 運作
firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0")

# geckodriver 的路徑
geckodriver_path = config['paths']['geckodriver_path']

# 建立 Service 物件
service = Service(geckodriver_path, log_path=os.devnull)

# 建立 WebDriver
driver = webdriver.Firefox(service=service, options=firefox_options)

# ===== 讀取 JSON 資料來源 =====
json_path = config['paths']['json_path']
if not os.path.exists(json_path):
    logging.error(f"找不到 JSON 檔案：{json_path}")
    sys.exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    try:
        sources = json.load(f)
        logging.info(f"共載入 {len(sources)} 筆資料來源")
    except json.JSONDecodeError as e:
        logging.error(f"JSON 格式錯誤：{e}")
        sys.exit(1)

# ===== 建立資料庫連線 =====
try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
except Exception as e:
    logging.error(f"資料庫連線失敗：{e}")
    driver.quit()
    sys.exit(1)

# ===== 爬取並寫入資料表 =====
for entry in sources:
    location_id = entry.get("id", "0")
    location_en = entry.get("location", "Unknown")
    location_tw = entry.get("location_zhtw", location_en)
    url = entry.get("source_url")
    
    if not url:
        logging.warning(f"{location_tw} 缺少 URL，略過")
        continue

    try:
        driver.get(url)
        driver.implicitly_wait(10)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        scripts = soup.find_all("script", {"type": "text/javascript"})

        # 輸出結果
        for script in scripts:
            report = json.dumps(script.string, ensure_ascii=False)
            

            ################### Debug Console ###########################
            # 觀查開啟的網頁是否正確
            logging.info(f"開啟網頁：{url}")
            # 確認 script 數量
            logging.info(f"共找到 {len(scripts)} 個 <script> 標籤")

            # 測試印出前 1 個 script 的內容
            if len(scripts) > 0:
                logging.debug(f"第一個 <script> 內容：\n{scripts[0].string[:500]}")

            # 如果需要手動檢查才繼續：
            input("🔍 已顯示第一個 script，請按 Enter 繼續...")

            # print report
            logging.info(f"回傳值：{report}")
            # 或者你可以加條件中斷（例如沒找到就終止）
            if len(scripts) == 0:
                logging.error("❌ 找不到任何 <script>，停止程式。")
                sys.exit(1)
            ############################################################


        # matched = False
        # for script in scripts:
        #     if script.string and "windData" in script.string:
        #         match = re.search(r'windData\s*=\s*(\{.*?\});', script.string, re.DOTALL)
        #         if match:
        #             try:
        #                 wind_data_json = match.group(1)
        #                 wind_data_dict = json.loads(wind_data_json)
        #                 content = json.dumps(wind_data_dict, ensure_ascii=False)
        #                 timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        #                 cursor.execute("""
        #                     INSERT INTO wp_wind_speed_data 
        #                     (location_id, location, location_zhtw, url, script_content, created_at)
        #                     VALUES (%s, %s, %s, %s, %s, %s)
        #                 """, (location_id, location_en, location_tw, url, content, timestamp))
        #                 conn.commit()
        #                 logging.info(f"{location_tw} ({location_en}) - 成功寫入 windData")
        #                 matched = True
        #                 break
        #             except Exception as e:
        #                 logging.warning(f"{location_tw} - windData JSON 解析失敗：{e}")
        #                 matched = True
        #                 break

        # if not matched:
        #     logging.warning(f"{location_tw} - 找不到 windData script 或解析失敗")

    except Exception as e:
        logging.error(f"{location_tw} - 無法讀取 {url}：{e}")

# ===== 結束清理 =====
driver.quit()
cursor.close()
conn.close()
logging.info("所有任務完成")
