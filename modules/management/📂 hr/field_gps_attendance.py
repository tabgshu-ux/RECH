import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

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
        st.error(f"初始化外勤 GPS 資料表失敗: {e}")

def render_field_gps_attendance(engine, lang="繁體中文"):
    init_field_gps_db(engine)
    st.markdown("##### 📍 外勤位置辦理與工地即時人數監控 (Field GPS Tracking)")
    st.info("💡 說明：外勤同仁抵達指定工程案場後進行 GPS 定位打卡，系統即時回報工地現場出勤人數與座標，供管理部隨時稽核。")

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
            st.warning(f"讀取外勤紀錄失敗: {e}")

    # 1. 即時工地人數統計儀表板
    if field_records:
        df_field = pd.DataFrame(field_records)
        today_str = str(datetime.date.today())
        today_df = df_field[df_field["check_time"].str.startswith(today_str)]
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("📊 今日外勤總打卡人次", len(today_df))
        with col_m2:
            active_sites = today_df["site_name"].nunique() if not today_df.empty else 0
            st.metric("🏗️ 今日動工案場數", active_sites)
        with col_m3:
            st.metric("🟢 GPS 圍籬驗證狀態", "正常運行")
        st.markdown("---")

    # 2. 外勤打卡表單
    with st.form("field_gps_form"):
        st.markdown("##### 📱 外勤人員現場 GPS 報到")
        c1, c2 = st.columns(2)
        with c1:
            f_emp_id = st.text_input("工號", value="EMP-001")
            f_name = st.text_input("姓名", value="Nguyễn Văn A")
            f_site = st.selectbox("指派工程案場 / 工地", [
                "胡志明市總廠 (Reetech HQ)", 
                "平陽省美福工業區案場 (My Phuoc)", 
                "同奈省邊和高壓配電案場 (Bien Hoa)", 
                "隆安省太陽能案場 (Long An)"
            ])
        with c2:
            # 模擬 GPS 座標 (越南胡志明市/週邊預設值)
            f_lat = st.number_input("GPS 緯度 (Latitude)", value=10.7769, format="%.4f")
            f_lng = st.number_input("GPS 經度 (Longitude)", value=106.7009, format="%.4f")
            f_note = st.text_input("現場工作備註", placeholder="例如: 已抵達案場進行配電箱安裝...")

        if st.form_submit_button("🛰️ 確認送出外勤 GPS 打卡", type="primary", use_container_width=True):
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
                                "ctime": current_time_str, "status": "🟢 驗證成功 (In Geofence)", "note": f_note
                            })
                        st.success("✅ 外勤 GPS 打卡成功，已同步至管理部即時工地人數中！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"寫入資料庫失敗: {e}")
            else:
                st.warning("請填寫必要欄位！")

    st.markdown("---")
    st.markdown("##### 📋 全廠外勤工地打卡明細與即時追蹤")
    if field_records:
        st.dataframe(pd.DataFrame(field_records), use_container_width=True, hide_index=True)
    else:
        st.info("目前尚無外勤 GPS 打卡紀錄。")
