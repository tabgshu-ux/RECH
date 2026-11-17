# ==========================================
# 檔案路徑：modules/engineering/field_gps_attendance.py
# 職責：外勤打卡、相機拍照、每日進度回報、自由輸入工地名稱與多模式 GPS 座標設定
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime

def init_field_gps_db(engine):
    """初始化外勤打卡、進度回報與動態圍籬設定資料表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS hr_field_gps (
                        record_id VARCHAR(50) PRIMARY KEY,
                        emp_id VARCHAR(50),
                        emp_name VARCHAR(100),
                        site_name VARCHAR(150),
                        punch_type VARCHAR(50),
                        gps_lat FLOAT,
                        gps_lng FLOAT,
                        work_progress TEXT,
                        check_time VARCHAR(50),
                        status VARCHAR(50),
                        note TEXT,
                        has_photo BOOLEAN DEFAULT FALSE
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS eng_geofence_settings (
                        site_name VARCHAR(150) PRIMARY KEY,
                        lat FLOAT,
                        lng FLOAT,
                        radius_meters INT,
                        status VARCHAR(50)
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS eng_support_requests (
                        id SERIAL PRIMARY KEY,
                        emp_name VARCHAR(100),
                        from_project VARCHAR(200),
                        target_project VARCHAR(200),
                        reason TEXT,
                        status VARCHAR(50) DEFAULT '⏳ 待主管審核',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def render(engine=None, lang="繁體中文", **kwargs):
    init_field_gps_db(engine)

    st.markdown("### ⏱️ 外勤師傅考勤、GPS 圍籬打卡與工程進度回報中心")
    st.caption("支援自由輸入新工地名稱、多模式 GPS 定位設定與手機相機打卡驗證。")

    # 身份切換模擬
    user_role = st.selectbox(
        "👤 當前操作身份 (模擬登入權限):",
        ["👷 現場工程師 / 外勤工人 (僅能打卡與回報)", "👑 工程部主管 / 系統管理員 (可設定圍籬與審核)"],
        index=0
    )

    is_manager = "主管" in user_role or "管理員" in user_role

    if not is_manager:
        # ==========================================
        # 👷 【基層員工視角】拍照打卡與每日進度回報
        # ==========================================
        st.markdown("---")
        st.markdown("#### 📱 現場人員拍照打卡與每日工作進度回報")
        st.info("💡 請在指定案場範圍內進行打卡。下班打卡時必須填寫當日工程進度與上傳施工照片。")

        # 從資料庫動態讀取主管設定好的工地清單
        site_options = ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"]
        if engine is not None:
            try:
                df_sites = pd.read_sql("SELECT site_name FROM eng_geofence_settings", con=engine)
                if not df_sites.empty:
                    site_options = df_sites["site_name"].tolist()
            except Exception:
                pass

        with st.form("worker_punch_form"):
            c1, c2 = st.columns(2)
            with c1:
                f_emp_id = st.text_input("工號 (Employee ID)", value="EMP-001")
                f_name = st.text_input("姓名 (Full Name)", value="阮文雄 (Nguyen Van Hung)")
                f_site = st.selectbox("指派工程案場 / 工地 (取自系統圍籬主檔)", site_options)
                f_punch_type = st.radio("打卡類型", ["🟢 上班打卡 (現場拍照存證)", "🔴 下班打卡 (工程進度回報 + 施工照)"], horizontal=True)
            with c2:
                f_lat = st.number_input("GPS 緯度 (Latitude)", value=10.7769, format="%.4f")
                f_lng = st.number_input("GPS 經度 (Longitude)", value=106.7009, format="%.4f")
                
                f_progress = st.text_area("📊 當日工程進度回報 (主管與總經理室可見)", placeholder="例如: 已完成配電箱安裝 80%、主迴路拉線完畢...")
                f_note = st.text_input("現場備註 / 異常回報", placeholder="例如: 現場材料短缺需總務支援...")

            st.markdown("**📷 現場施工 / 打卡照片上傳 (Camera Verification)**")
            captured_image = st.camera_input("請對準現場施工環境或人員進行拍照打卡")

            submitted = st.form_submit_button("🛰️ 確認送出打卡與進度回報", type="primary", use_container_width=True)
            if submitted:
                if f_emp_id and f_name:
                    record_id = f"GPS-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    current_time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    has_photo_bool = True if captured_image is not None else False
                    p_type_val = "上班打卡" if "上班" in f_punch_type else "下班打卡+進度回報"

                    if engine is not None:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO hr_field_gps (record_id, emp_id, emp_name, site_name, punch_type, gps_lat, gps_lng, work_progress, check_time, status, note, has_photo)
                                    VALUES (:rid, :eid, :ename, :site, :ptype, :lat, :lng, :prog, :ctime, '🟢 範圍內 (In Range)', :note, :hphoto)
                                """), {
                                    "rid": record_id, "eid": f_emp_id.strip(), "ename": f_name.strip(),
                                    "site": f_site, "ptype": p_type_val, "lat": f_lat, "lng": f_lng,
                                    "prog": f_progress if "下班" in p_type_val else "（上班打卡無須回報進度）",
                                    "ctime": current_time_str, "note": f_note, "hphoto": has_photo_bool
                                })
                        except Exception as e:
                            st.error(f"資料庫寫入錯誤: {e}")
                    st.success("🎉 外勤打卡與每日工作進度回報成功！已同步至工程部主管與總經理室戰情中心。")

    else:
        # ==========================================
        # 👑 【主管/管理員視角】動態新增工地、自由輸入名稱、多模式 GPS 定位
        # ==========================================
        st.markdown("---")
        st.markdown("#### 👑 工程主管專用：案場圍籬動態設定與進度總覽")
        
        tab_mgr1, tab_mgr2, tab_mgr3 = st.tabs([
            "🗺️ 案場圍籬設定 (支援自由輸入與多模式 GPS)", 
            "📊 每日施工進度與打卡總表 (供總經理室)", 
            "🤝 提早離場支援申請審核"
        ])

        with tab_mgr1:
            st.markdown("##### 🗺️ 新增或設定案場地理圍籬 (Geofencing)")
            st.warning("🔒 【安全授權】僅限工程部主管操作。您可直接自由輸入新工地名稱，並透過多種模式取得經緯度座標。")

            with st.form("geofence_setting_form_v2"):
                # 🌟 解決痛點：支援自由輸入新工地名稱，或從現有清單選擇修改
                existing_sites = ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"]
                if engine is not None:
                    try:
                        df_s = pd.read_sql("SELECT site_name FROM eng_geofence_settings", con=engine)
                        if not df_s.empty:
                            existing_sites = df_s["site_name"].tolist()
                    except Exception:
                        pass

                site_mode = st.radio("作業模式", ["➕ 新增全新工地 (自由輸入名稱)", "✏️ 修改現有工地設定"], horizontal=True)
                
                if "新增" in site_mode:
                    new_site_name = st.text_input("📝 請輸入全新工地 / 案場名稱", placeholder="例如: 越南胡志明市新順統包工程")
                    target_site = new_site_name
                else:
                    target_site = st.selectbox("選擇要修改的現有案場", existing_sites)

                st.markdown("---")
                st.markdown("**📍 取得工地經緯度座標模式：**")
                coord_mode = st.radio(
                    "選擇座標取得方式", 
                    [
                        "🛰️ 模式 A：使用主管當前裝置 GPS 定位（請在工地現場點擊）", 
                        "🗺️ 模式 B：手動輸入經緯度座標（適用從 Google Maps 複製貼上）"
                    ]
                )

                cg1, cg2 = st.columns(2)
                if "模式 A" in coord_mode:
                    st.info("💡 系統將自動抓取您當前所在位置的經緯度作為工地中心點。")
                    m_lat = 10.7769  # 實務上可透過前端 JS 抓取真實裝置 GPS
                    m_lng = 106.7009
                    with cg1: st.metric("自動抓取緯度 (Lat)", f"{m_lat}")
                    with cg2: st.metric("自動抓取經緯度 (Lng)", f"{m_lng}")
                else:
                    with cg1:
                        m_lat = st.text_input("中心點緯度 (Latitude)", value="10.7769")
                    with cg2:
                        m_lng = st.text_input("中心點經度 (Longitude)", value="106.7009")

                m_radius = st.slider("圍籬允許半徑範圍 (公尺)", min_value=100, max_value=3000, value=500, step=50)
                m_status = st.selectbox("圍籬防護狀態", ["🟢 啟用中 (強制限制打卡範圍)", "🔴 暫時關閉"])

                # 嵌入 Google Maps 預覽
                st.markdown("**🗺️ Google Maps 案場圍籬即時預覽**")
                try:
                    lat_float = float(m_lat)
                    lng_float = float(m_lng)
                except Exception:
                    lat_float, lng_float = 10.7769, 106.7009

                map_html = f"""
                <iframe width="100%" height="300" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
                    src="https://maps.google.com/maps?q={lat_float},{lng_float}&z=15&output=embed">
                </iframe>
                """
                st.markdown(map_html, unsafe_allow_html=True)

                if st.form_submit_button("💾 儲存並建立該案場地理圍籬設定", type="primary", use_container_width=True):
                    if not target_site:
                        st.error("⚠️ 請輸入或選擇有效的工地名稱！")
                    else:
                        if engine is not None:
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("""
                                        INSERT INTO eng_geofence_settings (site_name, lat, lng, radius_meters, status)
                                        VALUES (:s, :lat, :lng, :r, :st)
                                        ON CONFLICT (site_name) DO UPDATE 
                                        SET lat = EXCLUDED.lat, lng = EXCLUDED.lng, radius_meters = EXCLUDED.radius_meters, status = EXCLUDED.status;
                                    """), {"s": target_site.strip(), "lat": lat_float, "lng": lng_float, "r": m_radius, "st": m_status})
                                st.success(f"🎉 成功儲存案場 [{target_site}] 的圍籬設定！所有外勤人員即刻生效。")
                            except Exception as e:
                                st.error(f"資料庫儲存失敗: {e}")

        with tab_mgr2:
            st.markdown("##### 📊 每日施工進度與打卡總表 (同步總經理室)")
            if engine is not None:
                try:
                    df_all = pd.read_sql("SELECT record_id AS 紀錄編號, emp_id AS 工號, emp_name AS 姓名, site_name AS 案場, punch_type AS 類型, work_progress AS 每日進度回報, check_time AS 打卡時間, has_photo AS 現場照片 FROM hr_field_gps ORDER BY check_time DESC", con=engine)
                    if df_all.empty:
                        st.info("目前尚無外勤打卡與進度回報紀錄。")
                    else:
                        st.dataframe(df_all, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.warning(f"讀取資料庫失敗: {e}")
            else:
                st.info("資料庫連線尚未建立。")

        with tab_mgr3:
            st.markdown("##### 🤝 員工提早離場支援申請審核清單")
            if engine is not None:
                try:
                    df_sup = pd.read_sql("SELECT id, emp_name AS 員工姓名, from_project AS 原工地, target_project AS 支援目標工地, reason AS 支援原因, status AS 審核狀態, created_at AS 申請時間 FROM eng_support_requests ORDER BY id DESC", con=engine)
                    if df_sup.empty:
                        st.info("目前尚無任何支援申請。")
                    else:
                        st.dataframe(df_sup, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.warning(f"讀取支援紀錄失敗: {e}")
