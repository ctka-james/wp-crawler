# # 設定 Firefox 選項
# firefox_options = Options()
# firefox_options.add_argument("--headless")  # 無頭模式
# firefox_options.binary_location = "/usr/bin/firefox"

# # 設定 Firefox Profile（優化載入）
# firefox_options.set_preference("permissions.default.image", 2) # 不載入圖片
# firefox_options.set_preference("browser.display.use_document_colors", False) # 停用顏色
# firefox_options.set_preference("browser.display.use_document_fonts", 0) # 停用字型
# firefox_options.set_preference("javascript.enabled", True) # 保留 JS 運作
# firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0")

# # 建立 WebDriver
# driver = webdriver.Firefox(service=service, options=firefox_options)

# # url = 'https://www.cwb.gov.tw/V8/C/W/WindSpeed/MOD/plot/46705.html'
# # 由各點的windChart.php傳url字串給windChartCrawler()再傳給python處理內容
# # python接收後用sys.argv[1]代表url
# url = sys.argv[1]

import os
import sys
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

# 設定 Firefox 選項
firefox_options = Options()
firefox_options.add_argument("--headless")  # 無頭模式
firefox_options.binary_location = "/usr/bin/firefox"  # ← 加上這行，明確指定 Firefox 的執行檔

# 設定 Firefox Profile（優化載入）
firefox_options.set_preference("permissions.default.image", 2) # 不載入圖片
firefox_options.set_preference("browser.display.use_document_colors", False) # 停用顏色
firefox_options.set_preference("browser.display.use_document_fonts", 0) # 停用字型
firefox_options.set_preference("javascript.enabled", True) # 保留 JS 運作
firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0")

# geckodriver 的路徑
geckodriver_path = '/usr/local/bin/geckodriver'

# 建立 Service 物件
service = Service(geckodriver_path, log_path=os.devnull)

# 建立 WebDriver
driver = webdriver.Firefox(service=service, options=firefox_options)

# 打開爬取網頁
url = sys.argv[1] # 由php傳過來
#url = 'https://www.cwa.gov.tw/V8/C/W/WindSpeed/MOD/plot/C0UB1.html' # 蘇澳(可以urllib.request)
# url = 'https://www.cwa.gov.tw/V8/C/W/WindSpeed/MOD/plot/46705.html' # 新屋(不行urllib.request)
driver.get(url)

# 獲取頁面內容
dataInfo = driver.page_source

# 使用 BeautifulSoup 解析 HTML
root = BeautifulSoup(dataInfo, "html.parser")
data = root.find_all("script", {"type": "text/javascript"})

# 輸出結果
for script in data:
    report = json.dumps(script.string, ensure_ascii=True)
    print(report)
    # print(script.string)
# 關閉 WebDriver
driver.quit()
