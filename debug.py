################### Debug Console ###########################
# 印出已定義的變數
logging.info(f"{location_tw}=={location_en}==的id是：{location_id}")
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