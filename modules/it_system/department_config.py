# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：1~4 級動態組織配置中心（完整程式碼）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text, create_engine
import os
import time

def get_robust_db_engine(passed_engine=None):
    if passed_engine is not None:
        return passed_engine
    db_url = os.environ.get("SUPABASE_DB_URL") or st.secrets.get("SUPABASE_DB_URL", "")
    if db_url:
        try:
            clean_url = db_url.strip()
            if "pooler.supabase.com" in clean_url and "?" not in clean_url:
                clean_url += "?sslmode=require"
            return create_engine(clean_url, pool_pre_ping=True, connect_args={"prepare_threshold": None})
        except Exception:
            return None
    return None

def reset_and_init_db_tables(engine):
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_departments (
                        id SERIAL PRIMARY KEY,
                        dept_code VARCHAR(100) UNIQUE NOT NULL,
                        parent_code VARCHAR(100),
                        level_depth VARCHAR(50) DEFAULT 'L1',
                        dept_name_zh VARCHAR(150) NOT NULL,
                        dept_name_vi VARCHAR(150),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))

                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        id SERIAL PRIMARY KEY,
                        dept_code VARCHAR(100) NOT NULL,
                        module_name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def render(engine=None, lang="繁體中文", **kwargs):
    active_engine = get_robust_db_engine(engine)
    
    conn_status = False
    if active_engine is not None:
        try:
            with active_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            conn_status = True
            reset_and_init_db_tables(active_engine)
        except Exception:
            pass

    st.subheader("🏢 公司組織架構與 L1~L4 動態配置中心")
    st.info("在此動態維護公司組織架構與部門模組掛載。")

    tab_tree, tab_add, tab_manage = st.tabs([
        "🌳 現有組織樹狀檢視", 
        "➕ 新增 L1~L4 部門與模組掛載", 
        "📋 現有部門清單與模組調整"
    ])

    existing_l1_list = [("無 (獨立 L1 頂級部門)", "None")]
    if conn_status:
        try:
            df_l1 = pd.read_sql("SELECT dept_code, dept_name_zh FROM sys_departments WHERE is_active = TRUE AND (level_depth = 'L1' OR parent_code IS NULL OR parent_code = 'None')", con=active_engine)
            if not df_l1.empty:
                for _, r in df_l1.iterrows():
                    existing_l1_list.append((r['dept_name_zh'], r['dept_code']))
        except Exception:
            pass

    with tab_tree:
        st.markdown("##### 🌳 當前系統組織與掛載模組樹狀結構")
        if conn_status:
            try:
                df_tree = pd.read_sql("SELECT dept_code, dept_name_zh, level_depth, parent_code FROM sys_departments WHERE is_active = TRUE", con=active_engine)
                if df_tree.empty:
                    st.info("目前尚無任何部門資料。")
                else:
                    l1_rows = df_tree[df_tree["level_depth"] == "L1"]
                    for _, l1 in l1_rows.iterrows():
                        l1_mods = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :c"), con=active_engine, params={"c": l1['dept_code']})["module_name"].tolist()
                        with st.expander(f"📂 [L1] {l1['dept_name_zh']} ({len(l1_mods)} 個掛載模組)"):
                            for m in l1_mods:
                                st.markdown(f"  - 📌 {m}")
            except Exception as e:
                st.warning(f"載入樹狀結構提示: {e}")

    with tab_add:
        ALL_AVAILABLE_MODULES = {
            "👔 管理部與二級課室 (Management & Sub-depts)": {
                "管理部主管綜合戰情儀表板": "統合請假早退人員名單與採購花費",
                "人事行政課 — 員工檔案與履約管理": "維護員工個人履歷、護照、工作證與合約資料",
                "財務會計課 — 應收帳款管理 (AR)": "追蹤客戶專案工程款請款進度與收款紀錄",
                "財務會計課 — 越南稅務標準財報 (Thông tư 200)": "自動生成符合越南會計標準的法定報表"
            },
            "✍️ 跨部門電子簽核中心": {
                "跨部門電子簽核中心主控台": "統一管理全公司請假、採購與財務撥款簽核",
            },
            "📊 總經理室與戰情決策": {
                "總經理室戰情室": "彙整全廠營運績效、KPI 達成率與重大異常警示[cite: 22]",
                "AI 原料採購顧問與金屬行情": "即時分析 LME 銅價與原物料走勢提供採購建議[cite: 22]",
                "工程進度與異常即時監控": "全盤掌握各地工程案場進度與工安異常[cite: 22]",
                "財務與金流戰情摘要 (AR / AP & P&L)": "即時掌控應收應付帳款與 Thông tư 200 會計財報分析",
                "工程案場與金額佔比分析": "分析各類型工程（如高低壓配電盤、廠房機電）之案場數量與合約總金額佔比"
            },
            "🛠️ 工程與現場作業管理": {
                "工程主管戰情室與案場管理": "統籌各案場施工能量與進度回報",
                "工程專案報價系統": "針對高低壓配電盤及 MEP 工程進行快速報價"
            }
        }

        with st.form("add_dynamic_dept_form"):
            parent_selection = st.selectbox("上層所屬部門", options=[item[0] for item in existing_l1_list])
            parent_code = next(item[1] for item in existing_l1_list if item[0] == parent_selection)
            
            level_choice = st.selectbox("組織層級", ["L2 - 二級部門 / 課室", "L1 - 頂級大部門"])
            name_zh = st.text_input("部門繁體中文名稱 *", placeholder="例如: 總經理室")
            name_vi = st.text_input("部門越文名稱", placeholder="Ví dụ: Phòng Tổng Giám đốc")
            
            st.markdown("---")
            st.markdown("#### 🧩 勾選並掛載此部門可操作的業務模組：[cite: 16]")

            selected_department_modules = []
            for cat_name, mod_dict in ALL_AVAILABLE_MODULES.items():
                with st.expander(f"{cat_name} （包含 {len(mod_dict)} 項功能）", expanded=False):
                    for mod_name, mod_desc in mod_dict.items():
                        if st.checkbox(f"**{mod_name}** — 📝 *{mod_desc}*", key=f"chk_m_{mod_name}"):
                            selected_department_modules.append(mod_name)

            submitted = st.form_submit_button("💾 儲存組織設定並掛載模組", type="primary", use_container_width=True)
            
            if submitted:
                if not name_zh:
                    st.error("⚠️ 請填寫部門名稱！")
                else:
                    unique_code = f"dept_{int(time.time()*1000)}"
                    lvl_val = level_choice.split()[0]
                    if conn_status:
                        try:
                            with active_engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO sys_departments (dept_code, parent_code, level_depth, dept_name_zh, dept_name_vi, is_active)
                                    VALUES (:code, :parent, :lvl, :zh, :vi, TRUE)
                                """), {"code": unique_code, "parent": parent_code if parent_code != "None" else None, "lvl": lvl_val, "zh": name_zh.strip(), "vi": name_vi.strip()})
                                
                                for m_name in selected_department_modules:
                                    conn.execute(text("INSERT INTO sys_department_modules (dept_code, module_name) VALUES (:code, :m_name)"), {"code": unique_code, "m_name": m_name})
                            st.success(f"🎉 成功新增部門 [{name_zh}]！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 失敗: {e}")

    with tab_manage:
        st.markdown("##### 📋 現有部門清單與模組調整")
        if conn_status:
            try:
                df_existing = pd.read_sql("SELECT dept_code, dept_name_zh, level_depth FROM sys_departments WHERE is_active = TRUE", con=active_engine)
                if not df_existing.empty:
                    dept_options = {f"[{row['level_depth']}] {row['dept_name_zh']}": row["dept_code"] for _, row in df_existing.iterrows()}
                    selected_target = st.selectbox("🎯 選擇要調整的部門", list(dept_options.keys()))
                    target_code = dept_options[selected_target]
                    st.info(f"已選定代碼: {target_code}")
            except Exception:
                pass

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
