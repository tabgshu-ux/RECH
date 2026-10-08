import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 外勤 GPS 打卡與工程部工地人數監控模組多語系字典 (i18n)
# ----------------------------------------------------
FIELD_ATT_I18N = {
    "繁體中文": {
        "title": "📍 工程部 / 管理部 - 外勤 GPS 打卡與工地即時人數監控",
        "caption": "工地外勤人員透過 GPS 定位上下班打卡；工程部主管可即時即刻掌握各個案場（工地）的出工人數與在場名冊。",
        "tab_punch": "📱 外勤人員 GPS 打卡 (工地端)",
        "tab_manager": "📊 工程部主管 - 各工地即時出工人數統計",
        "tab_history": "📑 外勤打卡歷史紀錄與搜尋",
        "punch_header": "🟢 登記進入施工現場與 GPS 打卡",
        "manager_header": "📊 各工程案場即時出工人數與在場名冊 (Live Site Workforce)",
        "search_label": "🔍 搜尋外勤員工姓名或案場...",
        "lbl_emp": "技術與施工人員 *",
        "lbl_project": "專案代碼 / 工地名稱 *",
        "project_opts": [
            "PROJ-2026-配電盤安裝工程 (西寧廠A案場)", 
            "PROJ-2026-過路橋架工程 (海防廠B案場)", 
            "PROJ-2026-廠房高壓線路拉線 (統包案場)"
        ],
        "lbl_type": "打卡動作 *",
        "type_opts": ["上班簽到 (Check-In)", "下班簽退 (Check-Out)"],
        "lbl_work": "今日施作內容與工作說明 *",
        "work_ph": "例如: 執行配電盤主幹線纜電線絕緣測試。",
        "btn_punch": "🚀 送出 GPS 現場打卡",
        "success_punch": "✅ 員工 `{name}` 於案場 `{project}` 打卡成功！GPS 坐標已回報工程部。",
        "col_index": "STT",
        "col_code": "工號",
        "col_name": "姓名",
        "col_project": "案場名稱",
        "col_type": "類型",
        "col_time": "打卡時間",
        "col_gps": "GPS 坐標",
        "col_work": "工作內容"
    },
    "Tiếng Việt": {
        "title": "📍 Quản lý Chấm công GPS Ngoại tuyến & Giám sát Nhân sự Công trường",
        "caption": "Kỹ sư và công nhân công trường chấm công GPS; Trưởng phòng kỹ thuật giám sát số lượng nhân sự trực tiếp tại từng công trường.",
        "tab_punch": "📱 Chấm công GPS (Dành cho công nhân)",
        "tab_manager": "📊 Thống kê nhân sự trực công trường (Dành cho Quản lý)",
        "tab_history": "📑 Lịch sử chấm công ngoại tuyến",
        "punch_header": "🟢 Đăng ký vào công trường & Chấm công GPS",
        "manager_header": "📊 Thống kê số lượng nhân sự và danh sách tại từng công trường",
        "search_label": "🔍 Tìm kiếm theo tên nhân viên hoặc công trường...",
        "lbl_emp": "Nhân sự thi công *",
        "lbl_project": "Mã dự án / Tên công trường *",
        "project_opts": [
            "PROJ-2026-Lắp đặt tủ điện (Nhà máy Tây Ninh)", 
            "PROJ-2026-Hệ thống máng cáp (Nhà máy Hải Phòng)", 
            "PROJ-2026-Kéo cáp cao thế (Dự án ngoài)"
        ],
        "lbl_type": "Hành động *",
        "type_opts": ["Vào ca (Check-In)", "Tan ca (Check-Out)"],
        "lbl_work": "Nội dung công việc hôm nay *",
        "work_ph": "Ví dụ: Kiểm tra cách điện cáp nguồn chính.",
        "btn_punch": "🚀 Gửi chấm công GPS",
        "success_punch": "✅ Nhân viên `{name}` đã chấm công thành công tại `{project}`!",
        "col_index": "STT",
        "col_code": "Mã NV",
        "col_name": "Họ tên",
        "col_project": "Công trường",
        "col_type": "Loại",
        "col_time": "Thời gian",
        "col_gps": "Tọa độ GPS",
        "col_work": "Công việc"
    },
    "English": {
        "title": "GPS Field Attendance & Live Site Workforce Monitoring",
        "caption": "Field workers punch in via GPS; Engineering managers monitor real-time headcount and workforce per project site.",
        "tab_punch": "📱 Field GPS Attendance",
        "tab_manager": "📊 Manager - Live Site Workforce Stats",
        "tab_history": "📑 Field Attendance History",
        "punch_header": "🟢 Register Site Entry & GPS Punch",
        "manager_header": "📊 Real-time Site Workforce & Headcount Summary",
        "search_label": "🔍 Search Employee Name or Project...",
        "lbl_emp": "Field Technician / Worker *",
        "lbl_project": "Project Code / Site Name *",
        "project_opts": [
            "PROJ-2026-Switchgear Install (Tay Ninh Site)", 
            "PROJ-2026-Cable Tray (Hai Phong Site)", 
            "PROJ-2026-High Voltage Pulling (External Site)"
        ],
        "lbl_type": "Action Type *",
        "type_opts": ["Check-In", "Check-Out"],
        "lbl_work": "Today's Work Description *",
        "work_ph": "Example: Main busbar insulation testing.",
        "btn_punch": "🚀 Submit GPS Field Punch",
        "success_punch": "✅ Employee `{name}` checked in successfully at `{project}`!",
        "col_index": "No.",
        "col_code": "Emp ID",
        "col_name": "Name",
        "col_project": "Project Site",
        "col_type": "Type",
        "col_time": "Timestamp",
        "col_gps": "GPS Coordinates",
        "col_work": "Work Details"
    }
}

def render_field_attendance_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in FIELD_ATT_I18N else "繁體中文"
    L = FIELD_ATT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化外勤打卡資料庫
    if "field_attendance_db" not in st.session_state:
        st.session_state.field_attendance_db = [
            {
                "code": "EMP-003",
                "name": "李佑銘",
                "project": "PROJ-2026-配電盤安裝工程 (西寧廠A案場)",
                "type": "上班簽到",
                "time": "2026-10-08 08:05:00",
                "gps": "10.8231° N, 106.6297° E",
                "work": "西寧廠變壓器與配電盤基礎定位"
            },
            {
                "code": "EMP-004",
                "name": "阮文強",
                "project": "PROJ-2026-過路橋架工程 (海防廠B案場)",
                "type": "上班簽到",
                "time": "2026-10-08 08:15:00",
                "gps": "20.8449° N, 106.6881° E",
                "work": "海防廠車間過路橋架配管安裝"
            }
        ]

    tab_manager, tab_punch, tab_history = st.tabs([
        L["tab_manager"], L["tab_punch"], L["tab_history"]
    ])

    with tab_manager:
        st.markdown(f"### {L['manager_header']}")
        st.info("💡 **工程部主管專屬戰情**：系統自動依據各個案場即時統計當前在場施工人數與出勤名冊，點擊下方各案場可展開詳細名單。")

        # 彙整各案場的在場人數
        active_projects = [
            "PROJ-2026-配電盤安裝工程 (西寧廠A案場)", 
            "PROJ-2026-過路橋架工程 (海防廠B案場)", 
            "PROJ-2026-廠房高壓線路拉線 (統包案場)"
        ]

        # 計算每個案場目前有多少人簽到 (Check-In)
        site_headcounts = {}
        for proj in active_projects:
            checked_in_workers = [
                item for item in st.session_state.field_attendance_db 
                if item["project"] == proj and ("簽到" in item["type"] or "In" in item["type"])
            ]
            site_headcounts[proj] = checked_in_workers

        # 以卡片或指標呈現各工地人數
        cols = st.columns(len(active_projects))
        for idx, proj in enumerate(active_projects):
            count = len(site_headcounts[proj])
            with cols[idx]:
                st.metric(label=f"🏗️ {proj.split('(')[0]}", value=f"{count} 人在場", delta="🟢 施工中")

        st.markdown("---")
        st.markdown("### 📋 各案場詳細出勤與施工人員名冊")

        selected_site_filter = st.selectbox("選擇要檢視的工程案場 (Filter by Site)", ["全部案場 (All Sites)"] + active_projects)

        filtered_records = st.session_state.field_attendance_db
        if selected_site_filter != "全部案場 (All Sites)":
            filtered_records = [item for item in st.session_state.field_attendance_db if item["project"] == selected_site_filter]

        if filtered_records:
            mgr_display = []
            for idx, item in enumerate(filtered_records, 1):
                mgr_display.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_project"]: item["project"],
                    L["col_type"]: item["type"],
                    L["col_time"]: item["time"],
                    L["col_gps"]: item["gps"],
                    L["col_work"]: item["work"]
                })
            st.dataframe(pd.DataFrame(mgr_display), use_container_width=True)
        else:
            st.info("目前無符合條件的外勤出勤紀錄。")

    with tab_punch:
        st.markdown(f"### {L['punch_header']}")
        with st.form("form_field_gps_punch"):
            c1, c2 = st.columns(2)
            with c1:
                worker_name = st.text_input(L["lbl_emp"], value="李佑銘 (現場工程師)")
                project_name = st.selectbox(L["lbl_project"], L["project_opts"])
            with c2:
                punch_action = st.selectbox(L["lbl_type"], L["type_opts"])
                st.text_input("當前 GPS 坐標 (自動偵測)", value="10.8231° N, 106.6297° E (西寧廠區)", disabled=True)

            work_desc = st.text_area(L["lbl_work"], placeholder=L["work_ph"])

            if st.form_submit_button(L["btn_punch"], type="primary", use_container_width=True):
                now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                w_code = "EMP-033" if "李" in worker_name else "EMP-045"
                w_name = worker_name.split(" ")[0]

                st.session_state.field_attendance_db.insert(0, {
                    "code": w_code,
                    "name": w_name,
                    "project": project_name,
                    "type": punch_action,
                    "time": now_str,
                    "gps": "10.8231° N, 106.6297° E",
                    "work": work_desc if work_desc else "依主管交辦事項執行"
                })
                st.success(L["success_punch"].format(name=w_name, project=project_name))
                st.rerun()

    with tab_history:
        st.markdown(f"### {L['tab_history']}")
        search_q = st.text_input(L["search_label"], key="field_hist_search")
        
        hist_data = st.session_state.field_attendance_db
        if search_q:
            hist_data = [
                i for i in hist_data 
                if search_q.lower() in i["name"].lower() or search_q.lower() in i["project"].lower()
            ]

        if hist_data:
            h_display = []
            for idx, item in enumerate(hist_data, 1):
                h_display.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_project"]: item["project"],
                    L["col_type"]: item["type"],
                    L["col_time"]: item["time"],
                    L["col_gps"]: item["gps"],
                    L["col_work"]: item["work"]
                })
            st.dataframe(pd.DataFrame(h_display), use_container_width=True)
        else:
            st.info("目前無外勤歷史紀錄。")

def show(*args, **kwargs):
    render_field_attendance_page(*args, **kwargs)

def main(*args, **kwargs):
    render_field_attendance_page(*args, **kwargs)

def render_field_attendance(*args, **kwargs):
    render_field_attendance_page(*args, **kwargs)
