# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：1~4 級動態部門樹狀掛載、模組拼圖自由勾選指派、資料庫管理（已修正 PgBouncer 預備語句衝突）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text, create_engine
import os
import re

def get_robust_db_engine(passed_engine=None):
    if passed_engine is not None:
        return passed_engine
    db_url = os.environ.get("SUPABASE_DB_URL") or st.secrets.get("SUPABASE_DB_URL", "")
    if db_url:
        try:
            clean_url = db_url.strip()
            if "pooler.supabase.com" in clean_url and "?" not in clean_url:
                clean_url += "?sslmode=require"
            # 關鍵修正：加入 connect_args={"prepare_threshold": 0} 解決 Supabase Pooler 預備語句報錯
            return create_engine(clean_url, pool_pre_ping=True, connect_args={"prepare_threshold": 0})
        except Exception:
            return None
    return None

def reset_and_init_db_tables(engine):
    """初始化系統設定資料表與預設模組關聯"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 1. 建立標準 1~4 級動態部門表
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

                # 2. 部門模組掛載表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        id SERIAL PRIMARY KEY,
                        dept_code VARCHAR(100) NOT NULL,
                        module_name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))

                # 3. 企業識別品牌設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_branding (
                        id SERIAL PRIMARY KEY,
                        setting_key VARCHAR(100) UNIQUE NOT NULL,
                        setting_value TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))

                # 4. 資料庫動態串接設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_db_configs (
                        id SERIAL PRIMARY KEY,
                        db_name VARCHAR(100) UNIQUE NOT NULL,
                        connection_url TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))

                # 5. 第三方 API 閘道設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_api_configs (
                        id SERIAL PRIMARY KEY,
                        api_key_name VARCHAR(100) UNIQUE NOT NULL,
                        api_secret_value TEXT,
                        description TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"資料庫初始化重置失敗: {e}")

def get_department_module_tree(engine=None):
    """從資料庫動態取得完整部門與掛載模組樹狀結構"""
    active_engine = get_robust_db_engine(engine)
    dynamic_tree = {}
    
    if active_engine is not None:
        try:
            reset_and_init_db_tables(active_engine)
            with active_engine.connect() as conn:
                df_dept = pd.read_sql(text("SELECT dept_code, dept_name_zh FROM sys_departments WHERE is_active = TRUE"), con=conn)
                if not df_dept.empty:
                    for _, row in df_dept.iterrows():
                        d_code = row["dept_code"]
                        d_name = row["dept_name_zh"]
                        df_mod = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :d"), con=conn, params={"d": d_code})
                        mods = df_mod["module_name"].tolist() if not df_mod.empty else ["尚未掛載模組"]
                        dynamic_tree[d_name] = mods
                    return dynamic_tree
        except Exception:
            pass
            
    return {
        "總經理室 (Executive Office)": [
            "總經理室戰情室", 
            "AI 原料採購顧問與金屬行情", 
            "AR/AP 與 P&L 財務戰情儀表板", 
            "工程進度與異常即時監控", 
            "越南經營政策與法規動態"
        ],
        "管理部 (Management Dept)": [
            "公司公告佈告欄", 
            "員工檔案管理", 
            "員工打卡紀錄", 
            "員工薪資與保險", 
            "採購與應付帳款 (AP)", 
            "應收帳款管理 (AR)", 
            "越南稅務報表 (Thông tư 200)", 
            "電子發票管理"
        ]
    }

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

    st.subheader("🏢 公司部門架構與 1~4 級動態配置中心")
    st.info("在此動態維護公司組織架構，並可直接勾選指派對應的業務子模組。")

    if conn_status:
        if st.button("🗑️ [危險動作] 清空並重置所有部門與模組掛載資料表", type="secondary"):
            try:
                with active_engine.begin() as conn:
                    conn.execute(text("DROP TABLE IF EXISTS sys_department_modules CASCADE;"))
                    conn.execute(text("DROP TABLE IF EXISTS sys_departments CASCADE;"))
                reset_and_init_db_tables(active_engine)
                st.success("🎉 資料庫已成功完全清空並重新初始化！")
                st.rerun()
            except Exception as e:
                st.error(f"清空重置失敗: {e}")

    tab_tree, tab_add, tab_manage = st.tabs(["🌳 現有部門與模組樹狀檢視", "➕ 新增 1~4 級部門與模組掛載", "📋 現有部門清單與裁撤/停用管理"])

    with tab_tree:
        st.markdown("##### 🌳 當前系統一級部門與掛載子模組動態樹狀結構")
        tree_data = get_department_module_tree(active_engine)
        if not tree_data:
            st.info("目前尚無任何部門資料，請至「新增 1~4 級部門與模組掛載」分頁建立。")
        else:
            for dept, mods in tree_data.items():
                with st.expander(f"📁 {dept} ({len(mods)} 個掛載模組)"):
                    for m in mods:
                        st.markdown(f"- {m}")

    with tab_add:
        ALL_AVAILABLE_MODULES = {
            "📊 總經理室與戰情決策": [
                "總經理室戰情室", 
                "AI 原料採購顧問與金屬行情", 
                "AR/AP 與 P&L 財務戰情儀表板", 
                "工程進度與異常即時監控", 
                "越南經營政策與法規動態"
            ],
            "🛠️ 工程與現場作業管理": [
                "工程主管戰情室與案場管理",
                "工程專案報價系統", 
                "現場外勤打卡與作業登記",
                "施工日報表與點工點料登記", 
                "AI 施工照片辨識與安衛稽核",
                "工程證照與機具檢驗預警", 
                "配電盤電氣與機構設計圖庫",
                "BOM 零件與倉庫採購自動連動", 
                "外包商計價與工班管理",
                "FAT/SAT 出廠與現場驗收管理"
            ],
            "🏭 生產製造與倉儲管理": [
                "倉庫庫存與資材條碼管理",
                "板金加工組工單與條碼追蹤", 
                "粉體塗裝烤漆組品管",
                "配電盤組裝配線組進度追蹤",
                "工作廠區安全管理"
            ],
            "💰 財務、採購與稅務管理": [
                "採購與應付帳款 (AP)",
                "應收帳款管理 (AR)", 
                "越南稅務標準財務報表 (Thông tư 200)",
                "電子發票管理與 XML 歸檔"
            ],
            "👔 人事、行政與後勤支援": [
                "公司公告佈告欄", 
                "員工檔案管理", 
                "員工打卡紀錄", 
                "員工薪資與保險", 
                "宿舍與伙食管理", 
                "車輛進出口管制", 
                "車輛維修保養紀錄", 
                "固定資產與設備管理與文件管理"
            ]
        }

        with st.form("add_department_hierarchy_form"):
            parent_dept = st.selectbox(
                "上層所屬部門 (Parent Department)", 
                ["無 (根目錄 / 一級大部門)", "總經理室 (Executive Office)", "管理部 (Management Dept)", "工程部 (Engineering Dept)", "生產部 (Production Dept)", "倉庫管理 (Warehouse)", "簽核中心 (Approval Center)"]
            )
            
            level_choice = st.selectbox(
                "部門層級 (Hierarchy Level)", 
                [
                    "L1 - 大部門 / 事業處 (例如: 管理部、工程部、生產部)",
                    "L2 - 二級部門 / 課室 (例如: 人事行政課、總務採購課、板金製造課)",
                    "L3 - 三級組別 / 專案小組 (例如: 員工合約組、配電盤配線組)",
                    "L4 - 四級現場作業站 / 點工班 (例如: 西寧廠 A 區焊工班、外勤安裝班)"
                ]
            )
            
            name_zh = st.text_input("部門繁體中文名稱 *", placeholder="例如: 財務部, 人事行政課")
            name_vi = st.text_input("部門越文名稱 (Tiếng Việt)", placeholder="Ví dụ: Bộ phận Tài chính")
            
            st.markdown("---")
            st.markdown("#### 🧩 勾選並掛載此部門可操作的業務模組：")

            selected_department_modules = []
            for cat_name, mod_list in ALL_AVAILABLE_MODULES.items():
                with st.expander(f"{cat_name} （包含 {len(mod_list)} 項功能）", expanded=False):
                    for mod_item in mod_list:
                        if st.checkbox(mod_item, key=f"chk_dept_mod_{mod_item}"):
                            selected_department_modules.append(mod_item)

            st.markdown("---")
            submitted = st.form_submit_button("💾 儲存部門設定並掛載模組", type="primary", use_container_width=True)
            
            if submitted:
                if not name_zh:
                    st.error("⚠️ 請至少填寫部門繁體中文名稱！")
                else:
                    auto_code = re.sub(r'[^a-zA-Z0-9]', '_', name_zh.lower()) or "dept_node"
                    if conn_status:
                        try:
                            with active_engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO sys_departments (dept_code, parent_code, level_depth, dept_name_zh, dept_name_vi, is_active)
                                    VALUES (:code, :parent, :lvl, :zh, :vi, TRUE)
                                    ON CONFLICT (dept_code) DO UPDATE SET dept_name_zh = :zh, dept_name_vi = :vi, is_active = TRUE
                                """), {
                                    "code": auto_code,
                                    "parent": parent_dept.split()[0],
                                    "lvl": level_choice.split()[0],
                                    "zh": name_zh.strip(),
                                    "vi": name_vi.strip()
                                })
                                
                                conn.execute(text("DELETE FROM sys_department_modules WHERE dept_code = :code"), {"code": auto_code})
                                for m_name in selected_department_modules:
                                    conn.execute(text("""
                                        INSERT INTO sys_department_modules (dept_code, module_name)
                                        VALUES (:code, :m_name)
                                    """), {"code": auto_code, "m_name": m_name})

                            st.success(f"🎉 成功新增部門 [{name_zh}] 並掛載了 {len(selected_department_modules)} 個模組！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 寫入資料庫失敗: {e}")
                    else:
                        st.success(f"🎉 成功新增部門 [{name_zh}]（模擬模式）！")

    with tab_manage:
        st.markdown("##### 📋 現有部門與組織狀態清單")
        if conn_status:
            try:
                df_existing = pd.read_sql("SELECT dept_code as \"代碼\", level_depth as \"層級\", dept_name_zh as \"中文名稱\", dept_name_vi as \"越文名稱\" FROM sys_departments WHERE is_active = TRUE", con=active_engine)
                if not df_existing.empty:
                    st.dataframe(df_existing, use_container_width=True)
                else:
                    st.info("目前尚無部門資料。")
            except Exception:
                st.info("目前尚無部門資料。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
