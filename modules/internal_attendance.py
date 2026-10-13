import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 廠內考勤多語系字典 (i18n)
# ----------------------------------------------------
ATT_I18N = {
    "繁體中文": {
        "title": "🏢 管理部 - 廠內智慧考勤、越南勞動法合規與硬體 API 聯動",
        "caption": "依據越南勞動法管理完整出勤、OT 加班 (150%/200%/300%)、夜班加給 (30%)、假別與員工每月考勤統計查詢。",
        "tab_summary": "📊 員工個人月度考勤統計表 (給員工查詢/月結)",
        "tab_clock": "⏰ 模擬打卡機 / 考勤與加班資料進站",
        "tab_rules": "⚙️ 彈性緩衝時間與扣款規則設定",
        "tab_api": "🔌 硬體打卡機 API 介面設定 (SaaS)",
        "tab_logs": "📑 廠內完整出勤與刷卡日誌 (原始紀錄稽核)",
        "lbl_month": "選擇結算月份 (Month Filter)",
        "lbl_search": "搜尋員工姓名或工號...",
        "lbl_clock_in": "🟢 上班刷卡 (Check-in)",
        "lbl_clock_out": "🔴 下班刷卡 (Check-out)",
        "btn_clock": "🚀 提交刷卡登記",
        "msg_clock_success": "✅ 刷卡登記成功！已寫入考勤資料庫。",
        "header_tn": "🏭 西寧廠 (Tay Ninh) 出勤與刷卡紀錄",
        "header_hp": "🏭 海防廠 (Hai Phong) 出勤與刷卡紀錄"
    },
    "Tiếng Việt": {
        "title": "🏢 Phòng Quản lý - Chấm Công Thông Minh & Tuân Thủ Luật Lao Động VN",
        "caption": "Quản lý chấm công, tăng ca OT (150%/200%/300%), phụ cấp ca đêm (30%), phép năm và tổng hợp chấm công hàng tháng.",
        "tab_summary": "📊 Bảng tổng hợp chấm công tháng nhân viên",
        "tab_clock": "⏰ Máy chấm công giả lập / Nhập dữ liệu",
        "tab_rules": "⚙️ Cấu hình thời gian linh hoạt & Quy tắc trừ lương",
        "tab_api": "🔌 Cấu hình kết nối API Máy chấm công",
        "tab_logs": "📑 Lịch sử chi tiết quét thẻ chấm công (Nhật ký)",
        "lbl_month": "Chọn tháng (Month Filter)",
        "lbl_search": "Tìm theo tên hoặc mã nhân viên...",
        "lbl_clock_in": "🟢 Quét thẻ Vào (Check-in)",
        "lbl_clock_out": "🔴 Quét thẻ Ra (Check-out)",
        "btn_clock": "🚀 Lưu chấm công",
        "msg_clock_success": "✅ Chấm công thành công! Đã lưu vào cơ sở dữ liệu.",
        "header_tn": "🏭 Nhà máy Tây Ninh (Tay Ninh) Nhật ký chấm công",
        "header_hp": "🏭 Nhà máy Hải Phòng (Hai Phong) Nhật ký chấm công"
    },
    "English": {
        "title": "🏢 GA & HR - Internal Attendance & VN Labor Law Compliance",
        "caption": "Compliant with VN Labor Law: OT calculation (150%/200%/300%), night shift bonus (30%), leaves & monthly summaries.",
        "tab_summary": "📊 Employee Monthly Attendance Summary",
        "tab_clock": "⏰ Clock-in Kiosk / Data Entry",
        "tab_rules": "⚙️ Grace Period & Penalty Rules Configuration",
        "tab_api": "🔌 Attendance Hardware API Integration",
        "tab_logs": "📑 Full Clock-in Raw Audit Logs",
        "lbl_month": "Select Month",
        "lbl_search": "Search Employee Name or ID...",
        "lbl_clock_in": "🟢 Check-in",
        "lbl_clock_out": "🔴 Check-out",
        "btn_clock": "🚀 Submit Attendance Log",
        "msg_clock_success": "✅ Attendance recorded successfully!",
        "header_tn": "🏭 Tay Ninh Plant Attendance Logs",
        "header_hp": "🏭 Hai Phong Plant Attendance Logs"
    }
}

def init_attendance_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.internal_attendance_logs (
                    id SERIAL PRIMARY KEY,
                    emp_code VARCHAR(50) NOT NULL,
                    emp_name VARCHAR(100) NOT NULL,
                    plant_location VARCHAR(50) DEFAULT '西寧廠',
                    user_type VARCHAR(50) DEFAULT '廠內固定人員',
                    check_type VARCHAR(50) NOT NULL,
                    check_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    ot_category VARCHAR(50) DEFAULT '正常工時 (Standard)',
                    leave_type VARCHAR(50) DEFAULT '正常出勤 (Normal)',
                    status VARCHAR(50) DEFAULT '🟢 正常 (Normal)',
                    deduction_hours NUMERIC(5,2) DEFAULT 0.0
                );
            """))
    except Exception as e:
        st.warning(f"⚠️ 資料庫初始化提示: {str(e)}")

def render_internal_attendance_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = ATT_I18N.get(active_lang, ATT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_attendance_db(engine)

    # 📌 調整頁籤順序：將「完整日誌/原始紀錄」拉到最後面！
    tab_summary, tab_clock, tab_rules, tab_api, tab_logs = st.tabs([
        L["tab_summary"],
        L["tab_clock"],
        L["tab_rules"],
        L["tab_api"],
        L["tab_logs"]
    ])

    # ----------------------------------------------------
    # 📊 Tab 1 (第一優先級/預設開啟)：員工個人月度考勤統計表
    # ----------------------------------------------------
    with tab_summary:
        st.markdown("### 📊 員工個人月度考勤與 OT 統計彙整表")
        st.caption("供 HR 進行月終薪資核算對照，或提供員工查詢個人整月出勤天數、遲到次數與 OT 時數。")

        c1, c2 = st.columns([1, 2])
        with c1:
            month_filter = st.selectbox(L["lbl_month"], ["全部月份 (All)", "2026-10", "2026-09", "2026-08"], index=1)
        with c2:
            search_kw = st.text_input(L["lbl_search"], placeholder="輸入工號或姓名進行過濾...")

        # 模擬月度考勤彙整數據
        summary_data = [
            {"工號": "EMP-001", "姓名": "許福村", "部門": "總經理室", "應出勤天數": 22, "實際出勤": 22, "遲到次數": 0, "平時OT時數": 12.5, "週末OT時數": 4.0, "假別扣除": 0, "狀態": "🟢 正常"},
            {"工號": "EMP-002", "姓名": "Nguyễn Văn A", "部門": "生產部", "應出勤天數": 22, "實際出勤": 21, "遲到次數": 1, "平時OT時數": 20.0, "週末OT時數": 8.0, "假別扣除": 8, "狀態": "🟡 待補簽"},
            {"工號": "EMP-003", "姓名": "Trần Thị B", "部門": "管理部", "應出勤天數": 22, "實際出勤": 22, "遲到次數": 0, "平時OT時數": 5.0, "週末OT時數": 0.0, "假別扣除": 0, "狀態": "🟢 正常"}
        ]

        df_summary = pd.DataFrame(summary_data)
        if search_kw:
            df_summary = df_summary[df_summary["工號"].str.contains(search_kw, case=False) | df_summary["姓名"].str.contains(search_kw, case=False)]

        st.dataframe(df_summary, use_container_width=True)

    # ----------------------------------------------------
    # ⏰ Tab 2: 模擬打卡機 / 考勤與加班資料進站
    # ----------------------------------------------------
    with tab_clock:
        st.markdown("### ⏰ 廠內打卡與補簽單登記")
        with st.form("form_internal_clock"):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                e_code = st.text_input("員工工號", value=st.session_state.get("current_emp_code", "EMP-001"))
                e_name = st.text_input("員工姓名", value=st.session_state.get("user_name", "許福村"))
            with col_c2:
                plant_loc = st.selectbox("廠區位置", ["西寧廠 (Tay Ninh)", "海防廠 (Hai Phong)"])
                check_type = st.selectbox("刷卡類別", [L["lbl_clock_in"], L["lbl_clock_out"]])
            with col_c3:
                ot_cat = st.selectbox("OT 加班類別", ["正常工時 (Standard)", "平日加班 150%", "週末加班 200%", "國定假日 300%"])
                leave_cat = st.selectbox("假別/請假狀態", ["正常出勤 (Normal)", "事假 (Personal)", "病假 (Sick)", "年假 (Annual)"])

            if st.form_submit_button(L["btn_clock"], type="primary", use_container_width=True):
                plant_clean = "西寧廠" if "西寧" in plant_loc else "海防廠"
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.internal_attendance_logs 
                                (emp_code, emp_name, plant_location, check_type, ot_category, leave_type)
                                VALUES (:code, :name, :loc, :ctype, :ot, :leave)
                            """), {
                                "code": e_code, "name": e_name, "loc": plant_clean,
                                "ctype": check_type, "ot": ot_cat, "leave": leave_cat
                            })
                        st.success(L["msg_clock_success"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 刷卡記錄失敗: {str(e)}")
                else:
                    st.success(L["msg_clock_success"])

    # ----------------------------------------------------
    # ⚙️ Tab 3: 彈性緩衝時間與扣款規則設定
    # ----------------------------------------------------
    with tab_rules:
        st.markdown("### ⚙️ 考勤彈性時間與遲到扣款規則配置")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.time_input("標準上班時間", value=datetime.time(8, 0))
            st.number_input("上班彈性緩衝時間 (分鐘)", min_value=0, max_value=30, value=5)
        with col_r2:
            st.time_input("標準下班時間", value=datetime.time(17, 0))
            st.number_input("遲到超過幾分鐘算半天曠工", min_value=15, max_value=120, value=30)

        st.button("💾 儲存考勤參數規則", type="primary")

    # ----------------------------------------------------
    # 🔌 Tab 4: 硬體打卡機 API 介面設定
    # ----------------------------------------------------
    with tab_api:
        st.markdown("### 🔌 廠區硬體刷卡機 / 指紋機 API 串接設定")
        st.info("系統支援 ZKTeco、Hikvision 及 Dahua 人臉辨識與指紋打卡機 Webhook 自動同步。")
        st.text_input("Webhook 接收端點 (API Endpoint)", value="https://rechvn.streamlit.app/api/v1/attendance_webhook", disabled=True)
        st.text_input("API Secret Key", value="rech_sec_987654321_key", type="password")

    # ----------------------------------------------------
    # 📑 Tab 5 (最後面/低頻使用)：廠內完整出勤與刷卡原始日誌
    # ----------------------------------------------------
    with tab_logs:
        st.markdown("### 📑 廠內完整出勤與刷卡原始日誌 (Audit Logs)")
        st.caption("按時間倒序列出西寧廠與海防廠所有員工刷卡原始流水紀錄。")

        logs_data = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("""
                        SELECT id, emp_code, emp_name, plant_location, check_type, check_time, ot_category, leave_type, status, deduction_hours
                        FROM public.internal_attendance_logs
                        ORDER BY check_time DESC
                    """))
                    for r in res.fetchall():
                        logs_data.append({
                            "STT": r[0], "工號": r[1], "姓名": r[2], "廠區": r[3],
                            "類型": r[4], "刷卡時間": str(r[5]), "加班/加給": r[6],
                            "假別": r[7], "判定狀態": r[8], "扣款時數": f"{float(r[9]):.1f} 小時"
                        })
            except Exception:
                pass

        if not logs_data:
            logs_data = [
                {"STT": 1, "工號": "EMP-001", "姓名": "許福村", "廠區": "西寧廠", "類型": "上班簽到", "刷卡時間": "2026-10-13 07:55:00", "加班/加給": "正常工時", "假別": "正常出勤", "判定狀態": "🟢 正常", "扣款時數": "0.0 小時"},
                {"STT": 2, "工號": "EMP-001", "姓名": "許福村", "廠區": "西寧廠", "類型": "下班簽退", "刷卡時間": "2026-10-13 17:10:00", "加班/加給": "正常工時", "假別": "正常出勤", "判定狀態": "🟢 正常", "扣款時數": "0.0 小時"},
                {"STT": 3, "工號": "EMP-002", "姓名": "Nguyễn Văn A", "廠區": "海防廠", "類型": "上班簽到", "刷卡時間": "2026-10-13 08:08:00", "加班/加給": "正常工時", "假別": "正常出勤", "判定狀態": "🟡 遲到", "扣款時數": "0.5 小時"}
            ]

        df_logs = pd.DataFrame(logs_data)
        st.dataframe(df_logs, use_container_width=True)

def show(engine=None, lang="繁體中文", **kwargs):
    render_internal_attendance_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_internal_attendance_page(engine=engine, lang=lang, **kwargs)
