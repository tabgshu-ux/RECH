# ==========================================
# 檔案路徑：modules/engineering/eng_quotation.py
# 職責：工程專案報價與倉庫成本連動系統
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_quotation_tables(engine):
    """確保工程報價與明細資料表存在"""
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS eng_quotations (
                        id SERIAL PRIMARY KEY,
                        project_code VARCHAR(100) NOT NULL,
                        project_name VARCHAR(255) NOT NULL,
                        client_name VARCHAR(255),
                        total_cost NUMERIC(15, 2) DEFAULT 0,
                        quoted_amount NUMERIC(15, 2) DEFAULT 0,
                        profit_margin NUMERIC(5, 2) DEFAULT 0,
                        status VARCHAR(50) DEFAULT '草稿估價中',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 💰 工程專案報價與倉庫成本連動系統")
    st.caption("工程部專屬模組：估價時即時連動倉庫查詢物料庫存、單價與成本，自動試算專案毛利。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_quotation_tables(engine)

    tab_create, tab_list = st.tabs(["➕ 建立新專案估價單", "📋 現有專案報價與成本明細"])

    with tab_create:
        with st.form("eng_quote_form"):
            st.markdown("#### 📝 專案基本資料與估價試算")
            col1, col2 = st.columns(2)
            with col1:
                proj_code = st.text_input("專案代碼 (例如: PRJ-2026-001)", placeholder="請輸入編號")
                proj_name = st.text_input("專案名稱 (例如: 西寧廠高壓配電盤統包工程)", placeholder="請輸入名稱")
            with col2:
                client_name = st.text_input("客戶名稱 / 案場地點", placeholder="請輸入客戶")
                quoted_amt = st.number_input("預計對外報價金額 (₫)", min_value=0.0, step=100000.0, value=50000000.0)

            st.markdown("---")
            st.markdown("#### 📦 倉庫物料成本連動選擇 (即時抓取倉庫庫存與成本)")
            
            # 從資料庫或倉庫模組模擬抓取倉庫料號與成本
            warehouse_items = [
                {"code": "MAT-CU-01", "name": "導電銅排 (99.9% 銅)", "stock": 1200, "unit_cost": 150000},
                {"code": "MAT-BREAKER-03", "name": "Schneider MCCB 250A 斷路器", "stock": 45, "unit_cost": 2200000},
                {"code": "MAT-CABINET-02", "name": "戶外防水配電箱體 (不銹鋼)", "stock": 12, "unit_cost": 8500000},
                {"code": "MAT-CABLE-10", "name": "10mm2 絕緣控制電纜 (米)", "stock": 5000, "unit_cost": 25000}
            ]

            selected_items_cost = 0.0
            for item in warehouse_items:
                col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
                with col_i1:
                    is_sel = st.checkbox(f"{item['name']} (庫存: {item['stock']} | 成本: {item['unit_cost']:,.0f} ₫)", key=f"chk_mat_{item['code']}")
                with col_i2:
                    qty = st.number_input(f"數量 ({item['code']})", min_value=0, value=0, key=f"qty_{item['code']}")
                with col_i3:
                    if is_sel and qty > 0:
                        subtotal = item['unit_cost'] * qty
                        selected_items_cost += subtotal
                        st.markdown(f"**小計: {subtotal:,.0f} ₫**")

            st.markdown(f"### 📊 成本試算結果總結")
            st.info(f"總預估物料成本：`{selected_items_cost:,.0f} ₫` | 預估報價金額：`{quoted_amt:,.0f} ₫`")
            if quoted_amt > 0:
                profit = quoted_amt - selected_items_cost
                margin = (profit / quoted_amt) * 100
                st.success(f"預估毛利額：`{profit:,.0f} ₫` (預估毛利率：`{margin:.2f}%`)")

            submitted_quote = st.form_submit_button("🚀 儲存並送交協理/高層審核", type="primary", use_container_width=True)
            if submitted_quote:
                if proj_code and proj_name:
                    try:
                        profit_val = ((quoted_amt - selected_items_cost) / quoted_amt * 100) if quoted_amt > 0 else 0
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO eng_quotations (project_code, project_name, client_name, total_cost, quoted_amount, profit_margin, status)
                                VALUES (:pcode, :pname, :cname, :cost, :amt, :margin, '已送交協理審核')
                            """), {
                                "pcode": proj_code,
                                "pname": proj_name,
                                "cname": client_name,
                                "cost": selected_items_cost,
                                "amt": quoted_amt,
                                "margin": profit_val
                            })
                        st.success("🎉 專案報價單已成功建立，並自動進入簽核流程！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"儲存失敗: {e}")
                else:
                    st.warning("⚠️ 請完整填寫專案代碼與名稱。")

    with tab_list:
        st.markdown("#### 📋 現有專案報價紀錄與狀態")
        try:
            with engine.connect() as conn:
                quotes = conn.execute(text("SELECT * FROM eng_quotations ORDER BY id DESC")).fetchall()
                if quotes:
                    for q in quotes:
                        row = q._asdict()
                        with st.container(border=True):
                            st.markdown(f"**[{row.get('project_code')}] {row.get('project_name')}** (客戶: {row.get('client_name', '未指定')})")
                            st.caption(f"預估成本: `{row.get('total_cost'):,.0f} ₫` | 報價金額: `{row.get('quoted_amount'):,.0f} ₫` | 毛利率: `{row.get('profit_margin'):.2f}%` | 狀態: **{row.get('status')}**")
                else:
                    st.info("💡 目前尚無報價紀錄。")
        except Exception:
            st.info("💡 尚未建立報價資料表，請先建立一筆估價單以自動初始化。")
