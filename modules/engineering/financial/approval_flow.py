
# ==========================================
# 檔案路徑：modules/engineering/eng_approval_flow.py
# 職責：協理估價與副總/總經理高層簽核中心
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### ✍️ 協理估價與副總/總經理高層簽核中心")
    st.caption("多層級內控審批：協理提交專案估價後，依序呈報至副總與總經理進行金額核決與最終簽核。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫。")
        return

    tab_pending = st.tabs(["📥 待高層審核的專案估價單"])[0]

    with tab_pending:
        st.markdown("#### ⏳ 呈報至副總與總經理的待審案件")
        
        try:
            with engine.connect() as conn:
                quotes = conn.execute(text("SELECT * FROM eng_quotations WHERE status LIKE '%審核%' ORDER BY id DESC")).fetchall()
                if quotes:
                    for q in quotes:
                        row = q._asdict()
                        with st.container(border=True):
                            st.markdown(f"**專案: [{row.get('project_code')}] {row.get('project_name')}**")
                            st.caption(f"報價金額: `{row.get('quoted_amount'):,.0f} ₫` | 預估成本: `{row.get('total_cost'):,.0f} ₫` | 當前狀態: `{row.get('status')}`")
                            
                            col_app1, col_app2 = st.columns(2)
                            with col_app1:
                                if st.button("✅ 副總核准 (同意報價)", key=f"vp_approve_{row.get('id')}", use_container_width=True, type="primary"):
                                    with engine.begin() as conn_up:
                                        conn_up.execute(text("UPDATE eng_quotations SET status = '已獲副總核准，待總經理最終批示' WHERE id = :id"), {"id": row.get('id')})
                                    st.success("🎉 已通過副總審核，轉交總經理室！")
                                    st.rerun()
                            with col_app2:
                                if st.button("👑 總經理最終批示核准", key=f"gm_approve_{row.get('id')}", use_container_width=True, type="primary"):
                                    with engine.begin() as conn_up:
                                        conn_up.execute(text("UPDATE eng_quotations SET status = '總經理已最終核准 (可正式出單)' WHERE id = :id"), {"id": row.get('id')})
                                    st.success("🎉 總經理已正式批淮此專案報價！")
                                    st.rerun()
                else:
                    st.info("💡 目前沒有需要高層審核的待辦估價案件。")
        except Exception as e:
            st.info(f"💡 尚無關聯的報價審核資料表 ({e})。")
