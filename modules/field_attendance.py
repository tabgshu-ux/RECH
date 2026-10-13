import streamlit as st
import pandas as pd
import datetime
import os
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 現場外勤與工地即時人數控管多語系字典 (i18n)
# ----------------------------------------------------
FIELD_I18N = {
    "繁體中文": {
        "title_field": "📍 工程部 - 現場作業與工地外勤打卡登記",
        "caption_field": "供現場施工人員、工地主任進行每日 GPS 定位上下班打卡與現場工作回報。",
        "title_mgmt": "📊 管理部 - 跨案場外勤人數監控與出勤稽核中心",
        "caption_mgmt": "即時監控各工程案場在場人數、外勤津貼核算與出勤歷史軌跡穿透。",
        "tab_dashboard": "📊 各工程案場即時出工人數看板",
        "tab_checkin": "📝 現場外勤登記 (工地端)",
        "tab_history": "📋 外勤登記歷史紀錄與稽核搜尋",
        "lbl_site": "工程案場名稱 (Công trình)",
        "lbl_worker": "施工人員 / 工地主任",
        "lbl_type": "打卡類別",
        "lbl_work_type": "工作內容說明",
        "lbl_photo": "📸 上傳現場作業照片 (強制拍照存證)",
        "btn_submit_checkin": "🚀 提交外勤打卡登記",
        "msg_checkin_success": "✅ 外勤打卡登記成功！已寫入資料庫。",
        "msg_photo_required": "❌ 請務必拍照並上傳現場工作照片方可打卡！",
        "lbl_realtime_headcount": "各工程案場即時出工人數與在場名冊 (Live Site Workforce)",
        "lbl_filter_site": "選擇要檢視的工程案場 (Filter by Site)",
        "lbl_all_sites": "全部案場 (All Sites)"
    },
    "Tiếng Việt": {
        "title_field": "📍 Bộ phận Kỹ thuật - Chấm công & Báo cáo Công trường",
        "caption_field": "Dành cho nhân viên thi công, quản lý công trường chấm công GPS và báo cáo công việc hàng ngày.",
        "title_mgmt": "📊 Phòng Quản lý - Giám sát Quân số Công trường & Kiểm toán Chấm công",
        "caption_mgmt": "Giám sát thời gian thực số lượng nhân sự tại các công trường và đối soát lịch sử chấm công.",
        "tab_dashboard": "📊 Bảng quân số công trường thời gian thực",
        "tab_checkin": "📝 Chấm công ngoại hiện (Công trường)",
        "tab_history": "📋 Lịch sử chấm công & Tìm kiếm kiểm toán",
        "lbl_site": "Tên công trình / Dự án",
        "lbl_worker": "Nhân viên thi công / Giám sát",
        "lbl_type": "Loại chấm công",
        "lbl_work_type": "Mô tả nội dung công việc",
        "lbl_photo": "📸 Tải ảnh thi công thực tế (Bắt buộc)",
        "btn_submit_checkin": "🚀 Lưu đăng ký chấm công",
        "msg_checkin_success": "✅ Chấm công thành công! Đã lưu vào cơ sở dữ liệu.",
        "msg_photo_required": "❌ Bắt buộc phải chụp và tải ảnh tại công trường!",
        "lbl_realtime_headcount": "Quân số công trường thời gian thực & Danh sách hiện diện",
        "lbl_filter_site": "Lọc theo công trình",
        "lbl_all_sites": "Tất cả công trình (All Sites)"
    },
    "English": {
        "title_field": "📍 Engineering - Field Attendance & On-Site Check-in",
        "caption_field": "For site engineers and supervisors to submit daily GPS check-in and work logs.",
        "title_mgmt": "📊 GA & Management - Site Workforce Monitoring & Audit",
        "caption_mgmt": "Real-time monitoring of site headcounts, field allowance audits, and historical logs.",
        "tab_dashboard": "📊 Real-time Site Workforce Dashboard",
        "tab_checkin": "📝 Site Field Check-in",
        "tab_history": "📋 Attendance History & Audit Search",
        "lbl_site": "Project Site Name",
        "lbl_worker": "Worker / Site Manager",
        "lbl_type": "Check-in Type",
        "lbl_work_type": "Work Description",
        "lbl_photo": "📸 Upload Site Photo (Mandatory Evidence)",
        "btn_submit_checkin": "🚀 Submit Check-in Log",
        "msg_checkin_success": "✅ Check-in log successfully submitted to database!",
        "msg_photo_required": "❌ Photo evidence is mandatory for site check-in!",
        "lbl_realtime_headcount": "Real-time Site Headcount & Active Roster",
        "lbl_filter_site": "Filter by Project Site",
        "lbl_all_sites": "All Sites"
    }
}

# 預設模擬/初始化資料表
DEFAULT_SITES = [
    "PROJ-2026-配電盤安裝工程",
    "PROJ-2026-過路橋架工程",
    "PROJ-2026-廠房高壓線路拉線"
]

def init_field_attendance_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.field_attendance_logs (
                    id SERIAL PRIMARY KEY,
                    emp_code VARCHAR(50),
                    emp_name VARCHAR(100) NOT NULL,
                    site_name VARCHAR(150) NOT NULL,
                    check_type VARCHAR(50) NOT NULL,
                    work_desc TEXT,
                    photo_url TEXT,
                    location_gps VARCHAR(100),
                    check_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception as e:
        st.warning(f"⚠️ 資料庫初始化提示: {str(e)}")

# ----------------------------------------------------
# 📱 元件 1：工程部現場外勤打卡介面 (Field Worker View)
# ----------------------------------------------------
def render_field_checkin_form(engine, L, lang):
    st.markdown("#### 📝 新增外勤/工地現場打卡紀錄")
    
    UPLOAD_DIR = os.path.join("uploads", "field_photos")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with st.form("form_field_checkin"):
        c1, c2 = st.columns(2)
        with c1:
            site_selected = st.selectbox(L["lbl_site"], DEFAULT_SITES)
            worker_name = st.text_input(L["lbl_worker"], value=st.session_state.get("user_name", "工務人員"))
        with c2:
            check_type = st.selectbox(L["lbl_type"], ["🟢 上班打卡 (Check-in)", "🔴 下班打卡 (Check-out)", "⚡ 現場作業回報 (Work Log)"])
            curr_emp_code = st.session_state.get("current_emp_code", "EMP-001")

        work_desc = st.text_area(L["lbl_work_type"], placeholder="請填寫今日負責的配管、拉線或盤體測試內容...")
        photo_file = st.file_uploader(L["lbl_photo"], type=["jpg", "jpeg", "png"])

        if st.form_submit_button(L["btn_submit_checkin"], type="primary", use_container_width=True):
            if not photo_file:
                st.error(L["msg_photo_required"])
            else:
                # 保存圖片
                timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = os.path.join(UPLOAD_DIR, f"{timestamp_str}_{photo_file.name}")
                with open(file_path, "wb") as f:
                    f.write(photo_file.getbuffer())

                # 寫入資料庫 / Session
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO public.field_attendance_logs 
                                (emp_code, emp_name, site_name, check_type, work_desc, photo_url)
                                VALUES (:code, :name, :site, :ctype, :wdesc, :purl)
                            """), {
                                "code": curr_emp_code, "name": worker_name,
                                "site": site_selected, "ctype": check_type,
                                "wdesc": work_desc, "purl": file_path
                            })
                        st.success(L["msg_checkin_success"])
                    except Exception as e:
                        st.error(f"❌ 寫入資料庫失敗: {str(e)}")
                else:
                    if "field_attendance_db" not in st.session_state:
                        st.session_state.field_attendance_db = []
                    st.session_state.field_attendance_db.insert(0, {
                        "id": len(st.session_state.field_attendance_db) + 1,
                        "code": curr_emp_code, "name": worker_name,
                        "site": site_selected, "check_type": check_type,
                        "work_desc": work_desc, "photo_url": file_path,
                        "check_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success(L["msg_checkin_success"])

# ----------------------------------------------------
# 📊 元件 2：管理部人數統計與歷史稽核 (Management View)
# ----------------------------------------------------
def render_management_dashboard(engine, L, lang):
    st.markdown(f"### 📊 {L['lbl_realtime_headcount']}")

    # 讀取出勤紀錄
    records = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("""
                    SELECT id, emp_code, emp_name, site_name, check_type, work_desc, photo_url, check_time
                    FROM public.field_attendance_logs
                    ORDER BY check_time DESC
                """))
                for r in res.fetchall():
                    records.append({
                        "id": r[0], "code": r[1], "name": r[2], "site": r[3],
                        "check_type": r[4], "work_desc": r[5], "photo_url": r[6],
                        "check_time": str(r[7])
                    })
        except Exception:
            pass
    else:
        records = st.session_state.get("field_attendance_db", [
            {
                "id": 1, "code": "EMP-001", "name": "許福村", "site": "PROJ-2026-配電盤安裝工程",
                "check_type": "🟢 上班打卡 (Check-in)", "work_desc": "二次控制線路配線中",
                "photo_url": "", "check_time": "2026-10-13 08:00:00"
            },
            {
                "id": 2, "code": "EMP-002", "name": "Nguyễn Văn A", "site": "PROJ-2026-過路橋架工程",
                "check_type": "🟢 上班打卡 (Check-in)", "work_desc": "橋架安裝與固定",
                "photo_url": "", "check_time": "2026-10-13 08:15:00"
            }
        ])

    # 計算各案場在場人數卡片
    cols = st.columns(len(DEFAULT_SITES))
    for idx, site in enumerate(DEFAULT_SITES):
        site_users = [r for r in records if r["site"] == site and "上班" in r["check_type"]]
        cnt = len(site_users)
        cols[idx].metric(
            label=site.split("-")[-1],
            value=f"{cnt} 人在場",
            delta="🟢 施工中" if cnt > 0 else "⚪ 無人在場"
        )

    st.markdown("---")
    st.markdown("##### 📋 各案場詳細出勤與施工人員名冊")
    
    selected_site_filter = st.selectbox(L["lbl_filter_site"], [L["lbl_all_sites"]] + DEFAULT_SITES)
    
    filtered_records = records
    if selected_site_filter != L["lbl_all_sites"]:
        filtered_records = [r for r in records if r["site"] == selected_site_filter]

    if filtered_records:
        df_show = pd.DataFrame(filtered_records)
        st.dataframe(df_show[["check_time", "code", "name", "site", "check_type", "work_desc"]], use_container_width=True)
    else:
        st.info("目前尚無符合條件的外勤出勤紀錄。")

# ----------------------------------------------------
# 🚀 模組統一進入點 (支援 view_mode 路由隔離)
# ----------------------------------------------------
def render_field_attendance_page(engine=None, lang="繁體中文", view_mode="all", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = FIELD_I18N.get(active_lang, FIELD_I18N["繁體中文"])

    init_field_attendance_db(engine)

    # 📌 視圖分流 1：工程部現場端（僅顯示打卡登記，介面簡潔）
    if view_mode == "field_worker":
        st.title(L["title_field"])
        st.caption(L["caption_field"])
        render_field_checkin_form(engine, L, active_lang)

    # 📌 視圖分流 2：管理部主管端（僅顯示人數統計與歷史稽核名冊）
    elif view_mode == "management":
        st.title(L["title_mgmt"])
        st.caption(L["caption_mgmt"])
        render_management_dashboard(engine, L, active_lang)

    # 📌 視圖分流 3：系統管理員（顯示完整雙頁籤）
    else:
        st.title(L["title_mgmt"])
        tab1, tab2 = st.tabs([L["tab_dashboard"], L["tab_checkin"]])
        with tab1:
            render_management_dashboard(engine, L, active_lang)
        with tab2:
            render_field_checkin_form(engine, L, active_lang)

def show(engine=None, lang="繁體中文", view_mode="all", **kwargs):
    render_field_attendance_page(engine=engine, lang=lang, view_mode=view_mode, **kwargs)

def main(engine=None, lang="繁體中文", view_mode="all", **kwargs):
    render_field_attendance_page(engine=engine, lang=lang, view_mode=view_mode, **kwargs)
