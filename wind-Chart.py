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

# 讀取 config.conf
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.conf')
config.read(config_path)

# ======= 取得資料庫設定 =======
DB_HOST = config['database']['host']
DB_USER = config['database']['user']
DB_PASSWORD = config['database']['password']
DB_NAME = config['database']['name']

GECKODRIVER_PATH = '/usr/local/bin/geckodriver'
FIREFOX_BINARY = '/usr/bin/firefox'

# ======= 初始化 Selenium =======
firefox_options = Options()
firefox_options.add_argument("--headless")
firefox_options.binary_location = FIREFOX_BINARY
firefox_options.set_preference("permissions.default.image", 2)
firefox_options.set_preference("browser.display.use_document_colors", False)
firefox_options.set_preference("browser.display.use_document_fonts", 0)
firefox_options.set_preference("javascript.enabled", True)
firefox_options.set_preference("general.useragent.override", "Mozilla/5.0")

service = Service(GECKODRIVER_PATH, log_path=os.devnull)
driver = webdriver.Firefox(service=service, options=firefox_options)

# ======= 讀取 JSON 檔案 =======
# json_path = sys.argv[1]
json_path = config['paths']['json_path']

if not os.path.exists(json_path):
    print(f"[ERROR] 找不到 JSON 檔案：{json_path}")
    sys.exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    sources = json.load(f)

# ======= 建立資料庫連線 =======
print(sources)
sys.exit(0)
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8mb4'
)
cursor = conn.cursor()

# ======= 爬取每個地點網址並寫入資料表 =======
for entry in sources:
    location = entry.get("location")
    url = entry.get("url")
    if not url:
        continue

    try:
        driver.get(url)
        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        scripts = soup.find_all("script", {"type": "text/javascript"})
        
        for script in scripts:
            if script.string and "windData" in script.string:
                content = script.string.strip()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO wp_wind_speed_data (location, url, script_content, created_at)
                    VALUES (%s, %s, %s, %s)
                """, (location, url, content, timestamp))
                conn.commit()
                print(f"[INFO] {location} - 資料已儲存")
                break

    except Exception as e:
        print(f"[ERROR] {location} - {url} 讀取失敗: {e}")

driver.quit()
cursor.close()
conn.close()
