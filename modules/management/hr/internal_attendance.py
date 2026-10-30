import streamlit as st
import pandas as pd
from sqlalchemy import text

def get_t(lang):
    texts = {
        "繁體中文": {
            "title": "📊 員工打卡紀錄與出勤稽核中心",
            "info": "💡 說明：HR 可在此檢視廠內員工固定打卡紀錄，並透過分頁切換稽核外勤工程人員的 GPS 定位、工程進度與現場照片。",
            "tab1_title": "🏭 廠內固定考勤與月統計",
            "tab2_title": "📍 外勤 GPS 打卡與照片稽核",
            "no_field_data": "目前尚無外勤 GPS 打卡與回報紀錄。",
            "field_table_title": "📋 全廠外勤工程人員打卡明細總表"
        },
        "Tiếng Việt": {
            "title": "📊 Quản lý Chấm công & Kiểm toán Nhân viên",
            "info": "💡 Hướng dẫn: HR kiểm tra chấm công nhà xưởng và chuyển tab để duyệt GPS, tiến độ, ảnh hiện trường của nhân viên.",
            "tab1_title": "🏭 Chấm công Nhà xưởng & Thống kê",
            "tab2_title": "📍 Chấm công GPS & Kiểm duyệt Ảnh",
            "no_field_data": "Hiện tại chưa có dữ liệu chấm công GPS hiện trường.",
            "field_table_title": "📋 Bảng chi tiết chấm công hiện trường"
        }
    }
    return texts.get(lang, texts["繁體中文"])

def render_internal_attendance_page(engine=None, lang="繁體中文", **kwargs):
    t = get_t(lang)

    st.markdown(f"### {t['title']}")
    st.info(t['info'])

    # 建立雙 Tab 架構：將廠內考勤與外勤 GPS 打卡整合在同一個畫面中
    tab1, tab2 = st.tabs([t['tab1_title'], t['tab2_title']])

    # ----------------------------------------------------
    # TAB 1: 廠內固定考勤與月統計
    # ----------------------------------------------------
    with tab1:
        st.markdown("#### 🏢 廠內同仁出勤與月度 OT 統計")
        
        emp_records = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT emp_id, emp_name, department, position, base_salary FROM employee_profiles")).fetchall()
                    for r in res:
                        emp_records.append({
                            "工號": r[0], "姓名": r[1], "部門": r[2], "職稱": r[3],
                            "應出勤天數": 22, "實際出勤": 22, "遲到次數": 0, "平時OT時數": 0, "假日OT時數": 0, "狀態": "🟢 正常 (Normal)"
                        })
            except Exception:
                pass

        if not emp_records:
            emp_records = [
                {"工號": "VN-001", "姓名": "Nguyễn Văn A", "部門": "生產部", "職稱": "技術員", "應出勤天數": 22, "實際出勤": 22, "遲到次數": 0, "平時OT時數": 4, "假日OT時數": 0, "狀態": "🟢 正常 (Normal)"},
                {"工號": "VN-002", "姓名": "Tran Thi B", "部門": "管理部", "職稱": "會計專員", "應出勤天數": 22, "實際出勤": 21, "遲到次數": 1, "平時OT時數": 0, "假日OT時數": 0, "狀態": "🟡 遲到 1 次"},
            ]

        df_emp = pd.DataFrame(emp_records)
        st.dataframe(df_emp, use_container_width=True, hide_index=True)

    # ----------------------------------------------------
    # TAB 2: 外勤 GPS 打卡與照片稽核 (串連 hr_field_gps 資料表)
    # ----------------------------------------------------
    with tab2:
        st.markdown(f"#### {t['field_table_title']}")
        
        field_records = []
        if engine:
            try:
                with engine.connect() as conn:
                    res = conn.execute(text("SELECT record_id, emp_id, emp_name, site_name, punch_type, gps_lat, gps_lng, work_progress, check_time, status, note, has_photo FROM hr_field_gps ORDER BY check_time DESC")).fetchall()
                    for r in res:
                        field_records.append({
                            "紀錄編號": r[0], "工號": r[1], "姓名": r[2],
                            "案場": r[3], "打卡類型": r[4], "緯度": r[5], "經度": r[6],
                            "工程進度回報": r[7], "打卡時間": r[8], "狀態": r[9], "備註": r[10], "現場照片": "📷 已上傳" if r[11] else "無"
                        })
            except Exception as e:
                st.warning(f"載入外勤打卡資料庫發生錯誤 (DB tables initializing): {e}")

        if field_records:
            df_field = pd.DataFrame(field_records)
            st.dataframe(df_field, use_container_width=True, hide_index=True)
        else:
            st.info(t['no_field_data'])
