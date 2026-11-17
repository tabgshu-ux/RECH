# ==========================================
# 檔案路徑：modules/management/general_affairs/ehs_maintenance.py
# 職責：廠區設施維護、PCCC 消防安全檢查與環保廢棄物合約管理
# ==========================================

import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text

def init_table(engine):
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ga_ehs_records (
                        id SERIAL PRIMARY KEY,
                        item_name VARCHAR(150) NOT NULL,
                        category VARCHAR(50), 
                        inspection_date DATE,
                        next_due_date DATE,
                        status VARCHAR(50) DEFAULT '合格 (PASSED)',
                        responsible VARCHAR(100),
                        remarks TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"初始化 EHS 資料表失敗: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🧯 廠區設施維護與環安衛 (EHS) 合規管理")
    st.caption("越南公安消防 (PCCC) 檢查、環境資源廳 (DORE) 廢水廢棄物稽查與廠務水電修繕追蹤。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_table(engine)

    tab_dash, tab_add = st.tabs(["📊 EHS 檢點與證照合規總覽", "➕ 新增稽查與維護項目"])

    with tab_dash:
        st.markdown("#### 🚨 消防、環保與廠務設備檢点看板")
        try:
            with engine.connect() as conn:
                df = pd.read_sql("SELECT item_name as 檢點項目, category as 分類, inspection_date as 上次檢查日, next_due_date as 到期複檢日, status as 狀態, responsible as 負責人 FROM ga_ehs_records", conn)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    with engine.begin() as inner_conn:
                        inner_conn.execute(text("""
                            INSERT INTO ga_ehs_records (item_name, category, inspection_date, next_due_date, status, responsible, remarks)
                            VALUES 
                            ('全廠滅火器與消防栓檢點', '消防安全(PCCC)', '2026-10-01', '2026-12-01', '合格 (PASSED)', '總務課 - 阿發', '公安消防局每季抽檢合規'),
                            ('工業廢水處理設施與監測', '環保與廢水排放', '2026-11-01', '2026-11-30', '合格 (PASSED)', '工務課 - 阮文A', 'DORE 環資廳連線正常')
                            ON CONFLICT DO NOTHING;
                        """))
                    st.rerun()
        except Exception as e:
            st.error(f"讀取失敗: {e}")

    with tab_add:
        with st.form("ehs_form"):
            name = st.text_input("設備或檢點項目名稱")
            category = st.selectbox("分類", ["消防安全(PCCC)", "環保與廢水排放", "廠務水電與空調", "工廠安全稽查"])
            col1, col2 = st.columns(2)
            with col1:
                insp_date = st.date_input("上次檢點日期", value=date.today())
            with col2:
                due_date = st.date_input("下次複檢日期", value=date.today())
            
            resp = st.text_input("廠內負責人", value="總務課")
            remarks = st.text_area("合規備註說明")

            submitted = st.form_submit_button("💾 儲存 EHS 稽查項目", type="primary", use_container_width=True)
            if submitted and name:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO ga_ehs_records (item_name, category, inspection_date, next_due_date, responsible, remarks)
                            VALUES (:name, :cat, :insp, :due, :resp, :rem)
                        """), {"name": name, "cat": category, "insp": insp_date, "due": due_date, "resp": resp, "rem": remarks})
                    st.success("🎉 EHS 記錄已成功新增！")
                    st.rerun()
                except Exception as e:
                    st.error(f"新增失敗: {e}")
