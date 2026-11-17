# ==========================================
# 檔案路徑：modules/management/general_affairs/mro_assets_pr.py
# 職責：MRO 非生產性物料採購、固定資產管理與越南政府/工業區公關打點
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_table(engine):
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ga_government_pr (
                        id SERIAL PRIMARY KEY,
                        agency_name VARCHAR(150),
                        event_occasion VARCHAR(150),
                        budget_vnd DECIMAL(15, 2),
                        gift_description TEXT,
                        status VARCHAR(50) DEFAULT '已辦理',
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"初始化政府公關資料表失敗: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏛️ 行政採購 (MRO)、固定資產與政府公關 (PR)")
    st.caption("非生產性物料採購防弊、全廠固定資產盤點，以及與越南工業區管委會、公安、海關及稅務局之公關協調。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_table(engine)

    tab_pr, tab_mro, tab_asset = st.tabs(["🤝 政府與工業區公關 (PR)", "🛒 MRO 非生產性物料採購", "💻 固定資產與盤點管理"])

    with tab_pr:
        st.markdown("#### 🧧 當地政府機關與工業區公關互動記錄")
        try:
            with engine.connect() as conn:
                df = pd.read_sql("SELECT agency_name as 拜訪單位, event_occasion as 節慶或事由, budget_vnd as 預算金額VND, gift_description as 公關禮品與內容, status as 狀態 FROM ga_government_pr", conn)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    with engine.begin() as inner_conn:
                        inner_conn.execute(text("""
                            INSERT INTO ga_government_pr (agency_name, event_occasion, budget_vnd, gift_description, status)
                            VALUES 
                            ('Tay Ninh 工業區管委會 (Ban Quản lý KCN)', '越南春節 (Tết Nguyên Đán)', 15000000, '春節禮盒與茶葉禮品 (10份)', '已完成'),
                            ('地方消防警察大隊 (Phòng Cảnh sát PCCC)', '消防節公關拜訪', 8000000, '中秋禮盒打點', '已完成')
                            ON CONFLICT DO NOTHING;
                        """))
                    st.rerun()
        except Exception as e:
            st.error(f"讀取失敗: {e}")

        with st.form("pr_form"):
            agency = st.text_input("政府機關/工業區名稱", value="Tay Ninh 工業區管委會")
            occasion = st.text_input("事由 / 節慶", value="越南春節 (Tết)")
            budget = st.number_input("預算金額 (VND)", value=10000000, step=1000000)
            desc = st.text_area("公關禮品或協調事項說明")
            
            submitted = st.form_submit_button("💾 記錄政府公關項目", type="primary", use_container_width=True)
            if submitted and agency:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO ga_government_pr (agency_name, event_occasion, budget_vnd, gift_description)
                            VALUES (:ag, :occ, :bud, :desc)
                        """), {"ag": agency, "occ": occasion, "bud": budget, "desc": desc})
                    st.success("🎉 政府公關記錄已儲存！")
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

    with tab_mro:
        st.markdown("#### 📦 MRO 辦公文具、PPE 勞保用品與五金耗材請購")
        st.metric("本月 MRO 採購總金額", "42,500,000 VND", "較上月 -3.2%")

    with tab_asset:
        st.markdown("#### 💻 全廠固定資產與公務車輛盤點")
        st.info("💡 管理全廠辦公電腦、空調、會議設備及公務車輛編號。")
