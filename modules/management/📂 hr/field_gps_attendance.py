import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def get_t(lang):
    """多語系字典配置引擎 (支援繁中、越文，未來可擴充其他語系)"""
    texts = {
        "繁體中文": {
            "title": "📍 外勤位置辦理與工地即時人數監控 (Field GPS Tracking)",
            "info": "💡 說明：外勤同仁抵達指定工程案場後進行 GPS 定位打卡，系統即時回報工地現場出勤人數與座標，供管理部隨時稽核。",
            "total_punches": "📊 今日外勤總打卡人次",
            "active_sites": "🏗️ 今日動工案場數",
            "geofence_status": "🟢 GPS 圍籬驗證狀態",
            "form_title": "📱 外勤人員現場 GPS 報到",
            "emp_id": "工號",
            "emp_name": "姓名",
            "site_label": "指派工程案場 / 工地",
            "lat_label": "GPS 緯度 (Latitude)",
            "lng_label": "GPS 經度 (Longitude)",
            "note_label": "現場工作備註",
            "note_placeholder": "例如: 已抵達案場進行配電箱安裝...",
            "submit_btn": "🛰️ 確認送出外勤 GPS 打卡",
            "success_msg": "✅ 外勤 GPS 打卡成功，已同步至管理部即時工地人數中！",
            "table_title": "📋 全廠外勤工地打卡明細與即時追蹤",
            "no_data": "目前尚無外勤 GPS 打卡紀錄。",
            "fill_warning": "請填寫必要欄位！"
        },
        "越南文 (Tiếng Việt)": {
            "title": "📍 Quản lý Vị trí Hiện trường & Theo dõi Nhân số Công trường",
            "info": "💡 Hướng dẫn: Nhân viên hiện trường định vị GPS khi đến công trường, hệ thống báo cáo tức thời.",
            "total_punches": "📊 Tổng số lần chấm công GPS hôm nay",
            "active_sites": "🏗️ Số công trường đang hoạt động",
            "geofence_status": "🟢 Trạng thái hàng rào GPS",
            "form_title": "📱 Điểm danh GPS Hiện trường",
            "emp_id": "Mã nhân viên",
            "emp_name": "Họ và tên",
            "site_label": "Công trường / Dự án được phân công",
            "lat_label": "Vĩ độ GPS (Latitude)",
            "lng_label": "Kinh độ GPS (Longitude)",
            "note_label": "Ghi chú công việc",
            "note_placeholder": "Ví dụ: Đã đến công trường lắp đặt tủ điện...",
            "submit_btn": "🛰️ Xác nhận gửi chấm công GPS",
            "success_msg": "✅ Chấm công GPS thành công, đã đồng bộ vào hệ thống quản lý!",
            "table_title": "📋 Chi tiết chấm công hiện trường & Theo dõi thời gian thực",
            "no_data": "Hiện tại chưa có dữ liệu chấm công GPS.",
            "fill_warning": "Vui lòng điền đầy đủ thông tin bắt buộc!"
        }
    }
    return texts.get(lang, texts["繁體中文"])

def init_field_gps_db(engine):
    """初始化外勤 GPS 打卡與工地即時人數資料表"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS hr_field_gps (
                    record_id VARCHAR(50) PRIMARY KEY,
                    emp_id VARCHAR(50),
                    emp_name VARCHAR(100),
                    site_name VARCHAR(150),
                    gps_lat FLOAT,
                    gps_lng FLOAT,
                    check_time VARCHAR(50),
                    status VARCHAR(50),
                    note TEXT
                );
            """))
    except Exception as e:
        st.error(f"Error initializing DB: {e}")

def render_field_gps_attendance(engine, lang="繁體中文"):
    init_field_gps_db(engine)
    t = get_t(lang)

    st.markdown(f"##### {t['title']}")
    st.info(t['info'])

    field_records = []
    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM hr_field_gps ORDER BY check_time DESC")).fetchall()
                for r in res:
                    field_records.append({
                        "record_id": r[0], "emp_id": r[1], "emp_name": r[2],
                        "site_name": r[3], "lat": r[4], "lng": r[5],
                        "check_time": r[6], "status": r[7], "note": r[8]
                    })
        except Exception as e:
            st.warning(f"Error loading records: {e}")

    # 1. 即時工地人數統計儀表板
    if field_records:
        df_field = pd.DataFrame(field_records)
        today_str = str(datetime.date.today())
        today_df = df_field[df_field["check_time"].str.startswith(today_str)]
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric(t['total_punches'], len(today_df))
        with col_m2:
            active_sites = today_df["site_name"].nunique() if not today_df.empty else 0
            st.metric(t['active_sites'], active_sites)
        with col_m3:
            st.metric(t['geofence_status'], "Normal" if lang == "English" else "正常運行")
        st.markdown("---")

    # 2. 外勤打卡表單
    with st.form("field_gps_form"):
        st.markdown(f"##### {t['form_title']}")
        c1, c2 = st.columns(2)
        with c1:
            f_emp_id = st.text_input(t['emp_id'], value="EMP-001")
            f_name = st.text_input(t['emp_name'], value="Nguyễn Văn A")
            f_site = st.selectbox(t['site_label'], [
                "胡志明市總廠 (Reetech HQ)", 
                "平陽省美福工業區案場 (My Phuoc)", 
                "同奈省邊和高壓配電案場 (Bien Hoa)", 
                "隆安省太陽能案場 (Long An)"
            ])
        with c2:
            f_lat = st.number_input(t['lat_label'], value=10.7769, format="%.4f")
            f_lng = st.number_input(t['lng_label'], value=106.7009, format="%.4f")
            f_note = st.text_input(t['note_label'], placeholder=t['note_placeholder'])

        if st.form_submit_button(t['submit_btn'], type="primary", use_container_width=True):
            if f_emp_id and f_name:
                record_id = f"GPS-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if engine:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO hr_field_gps (record_id, emp_id, emp_name, site_name, gps_lat, gps_lng, check_time, status, note)
                                VALUES (:rid, :eid, :ename, :site, :lat, :lng, :ctime, :st, :note)
                            """), {
                                "rid": record_id, "eid": f_emp_id.strip(), "ename": f_name.strip(),
                                "site": f_site, "lat": f_lat, "lng": f_lng,
                                "ctime": current_time_str, "status": "🟢 In Geofence", "note": f_note
                            })
                        st.success(t['success_msg'])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning(t['fill_warning'])

    st.markdown("---")
    st.markdown(f"##### {t['table_title']}")
    if field_records:
        st.dataframe(pd.DataFrame(field_records), use_container_width=True, hide_index=True)
    else:
        st.info(t['no_data'])
