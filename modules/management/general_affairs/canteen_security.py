# ==========================================
# 檔案路徑：modules/management/general_affairs/canteen_security.py
# 職責：越籍員工食堂團膳監督、保全門禁秩序與廠區清潔管理
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
                    CREATE TABLE IF NOT EXISTS ga_canteen_feedback (
                        id SERIAL PRIMARY KEY,
                        feedback_date DATE,
                        meal_session VARCHAR(50),
                        food_quality_score INT,
                        hygiene_score INT,
                        feedback_comments TEXT,
                        action_taken TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"初始化食堂資料表失敗: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🍲 越籍員工後勤、食堂團膳與廠區秩序管理")
    st.caption("監督外包團膳廠商衛生與菜色品質、廠區保全門禁、車輛進出登記及環境清潔維護。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_table(engine)

    tab_canteen, tab_security = st.tabs(["🍛 食堂團膳滿意度與衛生稽核", "🛡️ 保全門禁與廠區秩序管理"])

    with tab_canteen:
        st.markdown("#### 🍚 每日伙食意見回饋與廠商監督")
        try:
            with engine.connect() as conn:
                df = pd.read_sql("SELECT feedback_date as 日期, meal_session as 餐別, food_quality_score as 菜色評分, hygiene_score as 衛生評分, feedback_comments as 意見反饋, action_taken as 總務處理結果 FROM ga_canteen_feedback", conn)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("💡 尚無伙食反饋記錄。")
        except Exception as e:
            st.error(f"讀取失敗: {e}")

        with st.form("canteen_form"):
            col1, col2 = st.columns(2)
            with col1:
                f_date = st.date_input("稽查日期", value=date.today())
                q_score = st.slider("菜色口味評分 (1-5星)", 1, 5, 4)
            with col2:
                session = st.selectbox("餐別", ["午餐 (Bữa trưa)", "晚餐 (Bữa tối)", "加班餐 (Bữa tăng ca)"])
                h_score = st.slider("環境衛生評分 (1-5星)", 1, 5, 5)
            
            comments = st.text_area("越籍員工意見回饋（中越雙語記錄）")
            action = st.text_input("總務與團膳廠商改善對策", value="已要求廠商加強保溫措施")

            submitted = st.form_submit_button("💾 提交食堂稽核與反饋", type="primary", use_container_width=True)
            if submitted:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO ga_canteen_feedback (feedback_date, meal_session, food_quality_score, hygiene_score, feedback_comments, action_taken)
                            VALUES (:fdate, :sess, :qscore, :hscore, :comm, :act)
                        """), {"fdate": f_date, "sess": session, "qscore": q_score, "hscore": h_score, "comm": comments, "act": action})
                    st.success("🎉 食堂稽核記錄已成功儲存！")
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

    with tab_security:
        st.markdown("#### 🚪 廠區保全、門禁巡檢與車輛管制")
        st.metric("今日廠區出入總人數", "482 人次", "正常")
        st.metric("今日出廠貨車放行單", "12 筆", "已全數核銷")
