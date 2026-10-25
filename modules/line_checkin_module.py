import streamlit as st
import pandas as pd
import datetime

def render_line_checkin_war_room(tenant):
    st.markdown("### 📱 越南外地工地打卡戰情室 (LINE & Zalo 雙軌串聯)")
    st.info("💡 針對越南在地員工全面習慣使用 Zalo、管理層習慣 LINE 的實際需求，系統支援雙軌 API 串聯。所有 Webhook 與 API 金鑰均聯動自【資訊管理 / IT】模組設定。")

    # 從 session_state 讀取在 IT 資訊管理模組中設定的 API 參數 (擴充支援 Zalo)
    if "it_api_settings" not in st.session_state:
        st.session_state.it_api_settings = {
            "line_channel_token": "API_TOKEN_NOT_CONFIGURED",
            "line_webhook_url": "https://api.reetech-erp.com/v1/webhook/line",
            "zalo_oa_token": "ZALO_TOKEN_NOT_CONFIGURED",
            "zalo_webhook_url": "https://api.reetech-erp.com/v1/webhook/zalo",
            "gps_radius_meters": 500
        }
    
    api_config = st.session_state.it_api_settings

    # 檢查 API 設定狀態
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        if api_config["line_channel_token"] == "API_TOKEN_NOT_CONFIGURED":
            st.warning("⚠️ LINE API 尚未在 IT 模組完整配置 (管理層通道)")
        else:
            st.success("🟢 LINE API 已連線 (管理層)")
    with col_stat2:
        if api_config["zalo_oa_token"] == "ZALO_TOKEN_NOT_CONFIGURED":
            st.warning("⚠️ Zalo OA API 尚未在 IT 模組完整配置 (越南員工通道)")
        else:
            st.success("🇻🇳 Zalo OA API 已成功串聯！(越南員工通道)")

    # 初始化打卡資料庫（加入通道來源標記：LINE 或 Zalo）
    if "line_checkin_records" not in st.session_state:
        st.session_state.line_checkin_records = [
            {"worker": "Nguyễn Văn Hùng (Kỹ thuật)", "channel": "🇻🇳 Zalo OA", "site": "胡志明市 A 廠區配電工程", "time": "2026-10-25 08:12", "gps": "10.7626° N, 106.6601° E", "status": "🟢 正常打卡"},
            {"worker": "Trần Văn Minh (Công nhân)", "channel": "🇻🇳 Zalo OA", "site": "平陽省 B 變壓器安裝工地", "time": "2026-10-25 08:30", "gps": "10.9804° N, 106.6519° E", "status": "🟢 正常打卡"},
            {"worker": "許福村 (台幹主管)", "channel": "📱 LINE", "site": "同奈省 C 廠區自動化配線", "time": "2026-10-25 08:45", "gps": "10.9574° N, 106.8427° E", "status": "🟢 正常打卡"}
        ]

    # 即時數據戰情看板
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("今日總出勤人數", f"{len(st.session_state.line_checkin_records) + 29} 人", "+3 較昨日")
    c2.metric("🇻🇳 Zalo 打卡佔比", "88.5%", "越南員工主力")
    c3.metric("📱 LINE 打卡佔比", "11.5%", "管理層/幹部")
    c4.metric("監控中工地數", "5 個", "全數連線中")

    st.markdown("---")
    st.markdown("#### 📋 各外地工地即時打卡名單與通訊來源記錄")
    df_checkin = pd.DataFrame(st.session_state.line_checkin_records)
    st.dataframe(df_checkin, use_container_width=True)

    with st.expander("🇻🇳 模擬越南員工透過 Zalo Mini App / OA 打卡測試"):
        with st.form("zalo_simulate_form_mod"):
            z_name = st.text_input("越南員工姓名 (Họ tên nhân viên)", value="Phạm Văn Đức (Thợ điện)")
            z_channel = st.selectbox("通訊打卡通道", ["🇻🇳 Zalo OA (越南員工)", "📱 LINE Official (台幹主管)"])
            z_site = st.selectbox("選擇當前所在工地 (Công trường)", [
                "胡志明市 A 廠區配電工程", 
                "平陽省 B 變壓器安裝工地", 
                "同奈省 C 廠區自動化配線"
            ])
            submits = st.form_submit_button("🚀 模擬 Zalo / LINE GPS 一鍵打卡送出", type="primary")
            if submits:
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.line_checkin_records.insert(0, {
                    "worker": z_name,
                    "channel": z_channel,
                    "site": z_site,
                    "time": now_str,
                    "gps": "10.7769° N, 106.7009° E (已通過圍籬驗證)",
                    "status": "🟢 正常打卡"
                })
                st.success("🎉 API 呼叫成功！打卡封包已透過 Zalo OA Webhook 寫入系統，人事與主管端看板已即時更新。")
                st.rerun()
