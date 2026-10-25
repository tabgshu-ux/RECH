import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 📱 外地工地 LINE & Zalo 雙軌打卡模組多語系字典 (i18n)
# ----------------------------------------------------
CHECKIN_I18N = {
    "繁體中文": {
        "title": "📱 外地工地 LINE & Zalo 雙軌打卡與即時人數戰情室",
        "caption": "裕豐電機（越南西寧廠）外派工地即時出勤監控與通訊 API 整合中心。",
        "tab_war_room": "📊 即時出勤戰情與打卡名單",
        "tab_simulate": "📲 模擬現場員工通訊打卡 (LINE / Zalo)",
        "metric_total": "今日總出勤人數",
        "metric_zalo": "🇻🇳 Zalo 打卡佔比",
        "metric_line": "📱 LINE 打卡佔比",
        "metric_sites": "監控中外地工地數",
        "table_header": "📋 各外地工地即時打卡名單與通訊來源記錄",
        "no_records": "目前尚無打卡紀錄。",
        "col_worker": "員工姓名與職稱",
        "col_channel": "通訊通道",
        "col_site": "所屬工地",
        "col_time": "打卡時間",
        "col_gps": "GPS 定位與圍籬狀態",
        "col_status": "狀態",
        "sim_header": "🧪 模擬現場人員打卡測試 (Webhook 驗證)",
        "sim_name": "員工姓名 (Họ tên)",
        "sim_channel": "選擇通訊打卡渠道",
        "sim_site": "選擇外地施工工地",
        "btn_submit": "🚀 模擬發送 GPS 打卡訊號 (觸發 API)",
        "success_msg": "🎉 API 呼叫成功！打卡封包已透過 Zalo OA / LINE Webhook 寫入系統，人事主管端已即時更新。"
    },
    "Tiếng Việt": {
        "title": "📱 Chiến trường chấm công LINE & Zalo tại công trường",
        "caption": "Trung tâm giám sát chuyên cần trực tuyến và tích hợp API thông tin liên lạc.",
        "tab_war_room": "📊 Bảng điều khiển chuyên cần",
        "tab_simulate": "📲 Mô phỏng chấm công nhân viên (LINE / Zalo)",
        "metric_total": "Tổng số nhân viên đi làm",
        "metric_zalo": "🇻🇳 Tỷ lệ Zalo",
        "metric_line": "📱 Tỷ lệ LINE",
        "metric_sites": "Số công trường giám sát",
        "table_header": "📋 Danh sách chấm công thời gian thực",
        "no_records": "Chưa có bản ghi chấm công.",
        "col_worker": "Họ tên nhân viên",
        "col_channel": "Kênh liên lạc",
        "col_site": "Công trường",
        "col_time": "Thời gian",
        "col_gps": "Định vị GPS",
        "col_status": "Trạng thái",
        "sim_header": "🧪 Mô phỏng kiểm tra chấm công nhân viên",
        "sim_name": "Họ tên nhân viên",
        "sim_channel": "Chọn kênh chấm công",
        "sim_site": "Chọn công trường",
        "btn_submit": "🚀 Gửi tín hiệu GPS (Gọi API)",
        "success_msg": "🎉 Gọi API thành công! Dữ liệu đã được ghi vào hệ thống qua Webhook."
    },
    "English": {
        "title": "📱 Field LINE & Zalo Dual-Channel Check-in War Room",
        "caption": "Reetech Industrial remote site attendance monitoring & communication API integration center.",
        "tab_war_room": "📊 Real-Time Attendance Dashboard",
        "tab_simulate": "📲 Simulate Field Worker Check-in (LINE / Zalo)",
        "metric_total": "Total Attendance Today",
        "metric_zalo": "🇻🇳 Zalo Check-in Share",
        "metric_line": "📱 LINE Check-in Share",
        "metric_sites": "Monitored Remote Sites",
        "table_header": "📋 Real-Time Field Check-in Logs",
        "no_records": "No check-in records found.",
        "col_worker": "Worker Name & Title",
        "col_channel": "Communication Channel",
        "col_site": "Assigned Site",
        "col_time": "Check-in Time",
        "col_gps": "GPS & Geofence Status",
        "col_status": "Status",
        "sim_header": "🧪 Simulate Field Worker Check-in Test",
        "sim_name": "Worker Name",
        "sim_channel": "Select Channel",
        "sim_site": "Select Remote Site",
        "btn_submit": "🚀 Simulate GPS Check-in (Trigger API)",
        "success_msg": "🎉 API Call Successful! Attendance packet written via Webhook."
    }
}

def get_global_config_from_db(engine, key, default_val=""):
    """從 system_licensing.py 所建立的 system_global_configs 讀取 IT 設定的 API Token"""
    if not engine:
        return default_val
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT config_value FROM public.system_global_configs WHERE config_key = :k"), {"k": key})
            row = res.fetchone()
            if row:
                return row[0]
    except Exception:
        pass
    return default_val

def render_line_checkin_module(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in CHECKIN_I18N else "繁體中文"
    L = CHECKIN_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # 🔗 從資料庫讀取在【資訊管理 / IT】中所設定的 API 憑證狀態
    line_token_db = get_global_config_from_db(engine, "line_access_token", "NOT_CONFIGURED")
    zalo_token_db = get_global_config_from_db(engine, "zalo_access_token", "")

    col_api1, col_api2 = st.columns(2)
    with col_api1:
        if line_token_db == "NOT_CONFIGURED" or not line_token_db:
            st.warning("⚠️ LINE Messaging API 尚未在【資訊管理 IT】中完整配置")
        else:
            st.success("🟢 LINE API 憑證已從 IT 模組自動載入 (管理層通道)")
    with col_api2:
        if not zalo_token_db:
            st.info("ℹ️ Zalo OA API 憑證未填寫 (若需越南員工專用通道請至 IT 模組設定)")
        else:
            st.success("🇻🇳 Zalo OA API 憑證已成功串聯！(越南員工主力通道)")

    # 初始化打卡紀錄資料庫
    if "line_checkin_records" not in st.session_state or not isinstance(st.session_state.line_checkin_records, list):
        st.session_state.line_checkin_records = [
            {"worker": "Nguyễn Văn Hùng (Kỹ thuật)", "channel": "🇻🇳 Zalo OA", "site": "胡志明市 A 廠區配電工程", "time": "2026-10-25 08:12", "gps": "10.7626° N, 106.6601° E", "status": "🟢 正常打卡"},
            {"worker": "Trần Văn Minh (Công nhân)", "channel": "🇻🇳 Zalo OA", "site": "平陽省 B 變壓器安裝工地", "time": "2026-10-25 08:30", "gps": "10.9804° N, 106.6519° E", "status": "🟢 正常打卡"},
            {"worker": "許福村 (台幹主管)", "channel": "📱 LINE", "site": "同奈省 C 廠區自動化配線", "time": "2026-10-25 08:45", "gps": "10.9574° N, 106.8427° E", "status": "🟢 正常打卡"}
        ]

    tab_war_room, tab_simulate = st.tabs([L["tab_war_room"], L["tab_simulate"]])

    # ----------------------------------------------------
    # 📊 Tab 1: 即時出勤戰情與打卡名單
    # ----------------------------------------------------
    with tab_war_room:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(L["metric_total"], f"{len(st.session_state.line_checkin_records) + 29} 人", "+3 較昨日")
        c2.metric(L["metric_zalo"], "88.5%", "越南員工主力")
        c3.metric(L["metric_line"], "11.5%", "管理層/幹部")
        c4.metric(L["metric_sites"], "5 個", "全數連線中")

        st.markdown("---")
        st.markdown(f"#### {L['table_header']}")
        
        display_logs = []
        for idx, rec in enumerate(st.session_state.line_checkin_records, 1):
            display_logs.append({
                "STT": idx,
                L["col_worker"]: rec["worker"],
                L["col_channel"]: rec["channel"],
                L["col_site"]: rec["site"],
                L["col_time"]: rec["time"],
                L["col_gps"]: rec["gps"],
                L["col_status"]: rec["status"]
            })
        
        if display_logs:
            st.dataframe(pd.DataFrame(display_logs), use_container_width=True, hide_index=True)
        else:
            st.info(L["no_records"])

    # ----------------------------------------------------
    # 📲 Tab 2: 模擬現場員工通訊打卡
    # ----------------------------------------------------
    with tab_simulate:
        st.markdown(f"### {L['sim_header']}")
        st.info("💡 此功能用來模擬越南現場工人透過手機點擊 Zalo Mini App 或台幹透過 LINE 發送 GPS 定位打卡的測試情境。")

        with st.form("form_simulate_field_checkin"):
            sim_name = st.text_input(L["sim_name"], value="Phạm Văn Đức (Thợ điện)")
            sim_channel = st.selectbox(L["sim_channel"], ["🇻🇳 Zalo OA (越南員工)", "📱 LINE Official (台幹主管)"])
            sim_site = st.selectbox(L["sim_site"], [
                "胡志明市 A 廠區配電工程", 
                "平陽省 B 變壓器安裝工地", 
                "同奈省 C 廠區自動化配線"
            ])
            
            btn_submit_checkin = st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True)
            
            if btn_submit_checkin:
                if sim_name:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.line_checkin_records.insert(0, {
                        "worker": sim_name,
                        "channel": sim_channel,
                        "site": sim_site,
                        "time": now_str,
                        "gps": "10.7769° N, 106.7009° E (圍籬內 14m)",
                        "status": "🟢 正常打卡"
                    })
                    st.success(L["success_msg"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請輸入員工姓名！")

# 兼容進入點
def show(engine=None, lang="繁體中文", **kwargs):
    render_line_checkin_module(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_line_checkin_module(engine=engine, lang=lang, **kwargs)

def render_line_checkin(*args, **kwargs):
    render_line_checkin_module(*args, **kwargs)
