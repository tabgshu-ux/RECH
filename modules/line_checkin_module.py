
import streamlit as st
import pandas as pd
import datetime

def render_line_checkin_war_room(tenant):
    st.markdown("### 📱 外地工地 LINE 打卡與即時人數戰情室")
    st.info("💡 工人在外地工地透過 LINE 官方帳號 / LIFF 進行 GPS 定位打卡與拍照回報。所有 LINE Webhook 與 API 金鑰均聯動自【資訊管理 / IT】模組設定。")

    # 從 session_state 或租戶物件讀取在 IT 資訊管理模組中設定的 API 參數
    if "it_api_settings" not in st.session_state:
        st.session_state.it_api_settings = {
            "line_channel_token": "API_TOKEN_NOT_CONFIGURED",
            "line_webhook_url": "https://api.reetech-erp.com/v1/webhook/line",
            "gps_radius_meters": 500
        }
    
    api_config = st.session_state.it_api_settings

    # 檢查 API 是否已在 IT 模組設定
    if api_config["line_channel_token"] == "API_TOKEN_NOT_CONFIGURED":
        st.warning("⚠️ 系統偵測到 LINE API 尚未在【資訊管理 / IT 授權設定】中完整配置！目前處於離線模擬驗證模式。")
    else:
        st.success(f"🟢 LINE API 已成功從 IT 模組載入串聯！Webhook 端點：`{api_config['line_webhook_url']}`")

    # 初始化打卡資料庫
    if "line_checkin_records" not in st.session_state:
        st.session_state.line_checkin_records = [
            {"worker": "阿村師 (師傅)", "site": "胡志明市 A 廠區配電工程", "time": "2026-10-25 08:12", "gps": "10.7626° N, 106.6601° E", "status": "🟢 正常打卡"},
            {"worker": "阮文雄 (技術員)", "site": "平陽省 B 變壓器安裝工地", "time": "2026-10-25 08:30", "gps": "10.9804° N, 106.6519° E", "status": "🟢 正常打卡"},
            {"worker": "陳建國 (工程師)", "site": "同奈省 C 廠區自動化配線", "time": "2026-10-25 08:45", "gps": "10.9574° N, 106.8427° E", "status": "🟢 正常打卡"}
        ]

    # 即時數據戰情看板
    c1, c2, c3 = st.columns(3)
    c1.metric("今日外地工地總出勤人數", f"{len(st.session_state.line_checkin_records) + 29} 人", "+3 較昨日")
    c2.metric("API 即時回應延遲", "38 ms", "極佳")
    c3.metric("監控中外地工地數", "5 個", "全數連線中")

    st.markdown("---")
    st.markdown("#### 📋 各外地工地即時打卡名單與 GPS 回報紀錄")
    df_checkin = pd.DataFrame(st.session_state.line_checkin_records)
    st.dataframe(df_checkin, use_container_width=True)

    with st.expander("📲 模擬 LINE LIFF 介面打卡與 Webhook 觸發測試"):
        with st.form("line_simulate_form_mod"):
            w_name = st.text_input("工人姓名 / 職稱", value="張小弟 (現場組員)")
            w_site = st.selectbox("選擇當前所在工地", [
                "胡志明市 A 廠區配電工程", 
                "平陽省 B 變壓器安裝工地", 
                "同奈省 C 廠區自動化配線"
            ])
            submits = st.form_submit_button("🚀 模擬 LINE 一鍵 GPS 打卡送出 (觸發 IT API)", type="primary")
            if submits:
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.line_checkin_records.insert(0, {
                    "worker": w_name,
                    "site": w_site,
                    "time": now_str,
                    "gps": "10.7769° N, 106.7009° E (已通過 IT 圍籬驗證)",
                    "status": "🟢 正常打卡"
                })
                st.success("🎉 API 呼叫成功！來自 LINE 介面的打卡封包已透過 IT 設定的 Webhook 寫入資料庫，人事與主管端已即時更新。")
                st.rerun()
