# ==========================================
# 檔案路徑：modules/management/general_affairs/expat_support.py
# 職責：台籍幹部後勤支援、簽證與證件到期預警（Work Permit / TRC）
# ==========================================

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from sqlalchemy import text

def init_table(engine):
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ga_expat_profiles (
                        id SERIAL PRIMARY KEY,
                        expat_name VARCHAR(150) NOT NULL,
                        passport_no VARCHAR(50),
                        nationality VARCHAR(50) DEFAULT '台灣 (Taiwan)',
                        work_permit_no VARCHAR(100),
                        work_permit_expiry DATE,
                        trc_no VARCHAR(100),
                        trc_expiry DATE,
                        visa_expiry DATE,
                        dormitory_room VARCHAR(50),
                        contact_phone VARCHAR(50),
                        notes TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"初始化台幹證件資料表失敗: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🛂 台籍幹部證件合規與後勤生活支援")
    st.caption("管理台幹工作證 (Work Permit)、暫住證 (TRC)、簽證效期到期智慧預警，以及宿舍分配與生活後勤。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_table(engine)

    tab_list, tab_add = st.tabs(["📋 台幹檔案與證件清單", "➕ 新增/編輯台幹資料"])

    with tab_list:
        try:
            with engine.connect() as conn:
                df = pd.read_sql("SELECT expat_name as 姓名, passport_no as 護照號碼, work_permit_no as 工作證號, work_permit_expiry as 工作證到期日, trc_no as 暫住證TRC, trc_expiry as TRC到期日, dormitory_room as 宿舍房號 FROM ga_expat_profiles", conn)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("💡 目前尚無台幹資料，請至右側分頁新增。")
        except Exception as e:
            st.error(f"讀取失敗: {e}")

    with tab_add:
        with st.form("expat_form"):
            name = st.text_input("台幹姓名")
            col1, col2 = st.columns(2)
            with col1:
                passport = st.text_input("護照號碼")
                wp_no = st.text_input("工作證編號 (Work Permit)")
                wp_exp = st.date_input("工作證到期日", value=date.today() + timedelta(days=180))
            with col2:
                room = st.text_input("宿舍房號 (如: A-201)")
                trc_no = st.text_input("暫住證號 (TRC)")
                trc_exp = st.date_input("TRC 暫住證到期日", value=date.today() + timedelta(days=180))
            
            visa_exp = st.date_input("商務簽證到期日", value=date.today() + timedelta(days=90))
            notes = st.text_area("後勤備註（如飲食喜好、特殊需求）")

            submitted = st.form_submit_button("💾 儲存台幹後勤與證件資料", type="primary", use_container_width=True)
            if submitted and name:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO ga_expat_profiles (expat_name, passport_no, work_permit_no, work_permit_expiry, trc_no, trc_expiry, visa_expiry, dormitory_room, notes)
                            VALUES (:name, :pass, :wp, :wpexp, :trc, :trcexp, :visa, :room, :notes)
                        """), {
                            "name": name, "pass": passport, "wp": wp_no, "wpexp": wp_exp,
                            "trc": trc_no, "trcexp": trc_exp, "visa": visa_exp, "room": room, "notes": notes
                        })
                    st.success("🎉 台幹資料與證件追蹤已成功建立！")
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存失敗: {e}")
