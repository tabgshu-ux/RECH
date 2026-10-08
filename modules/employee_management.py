# 強制轉換為越南當地時間 (UTC+7)
                vn_time = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
                now_str = vn_time.strftime("%Y-%m-%d %H:%M:%S")
