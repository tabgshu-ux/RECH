# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：1~4 級動態組織配置中心（已修復 Checkbox Key 重複報錯）
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

    # 🌟 使用帶有分類字首的 key，避免跨分類重複報錯
    ALL_AVAILABLE_MODULES = {
        "👔 管理部總覽與支援": [
            ("管理部總覽", "mgmt_ov"),
            ("公司公告佈告欄", "mgmt_ann"),
            ("人事行政課 — 員工檔案與履約管理", "mgmt_hr"),
            ("人事行政課 — 考勤與打卡紀錄", "mgmt_att"),
            ("人事行政課 — 薪資計算與 BHXH 保險", "mgmt_pay"),
            ("總務採購課 — 採購單與應付帳款 (AP)", "mgmt_ap")
        ],
        "📊 總經理室總覽與決策": [
            ("總經理室總覽", "gm_ov"),
            ("AI 原料採購顧問與金屬行情", "gm_ai"),
            ("工程進度與異常即時監控", "gm_prog"),
            ("財務與金流總覽 (AR / AP & P&L)", "gm_fin"),
            ("工程案場與金額佔比分析", "gm_anal"),
            ("工程專案損益與預算控管", "gm_pnl")
        ],
        "🛠️ 工程部總覽與作業": [
            ("工程部總覽", "eng_ov"),
            ("工程專案損益與預算控管", "eng_pnl"),
            ("工程專案報價系統", "eng_quote"),
            ("施工日報表與點工點料登記", "eng_log"),
            ("配電盤電氣與機構設計圖庫", "eng_cad")
        ],
        "🏭 生產製造與倉儲管理": [
            ("生產部總覽", "prod_ov"),
            ("倉庫庫存與資材條碼管理", "prod_wms"),
            ("配電盤組裝配線組進度追蹤", "prod_asm")
        ]
    }

    with tab_tree:
        st.markdown("##### 🌳 當前系統組織與掛載模組樹狀結構")
        if conn_status:
            try:
                df_tree = pd.read_sql("SELECT dept_code, dept_name_zh, level_depth, parent_code FROM sys_departments WHERE is_active = TRUE", con=active_engine)
                if not df_tree.empty:
                    l1_rows = df_tree[df_tree["level_depth"] == "L1"]
                    for _, l1 in l1_rows.iterrows():
                        l1_mods = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :c"), con=active_engine, params={"c": l1['dept_code']})["module_name"].tolist()
                        with st.expander(f"📂 [L1] {l1['dept_name_zh']} ({len(l1_mods)} 個掛載模組)"):
                            for m in l1_mods:
                                st.markdown(f"  - 📌 {m}")
            except Exception as e:
                st.warning(f"載入樹狀結構提示: {e}")

    with tab_add:
        with st.form("add_dynamic_dept_form"):
            parent_selection = st.selectbox("上層所屬部門", options=[item[0] for item in existing_l1_list])
            parent_code = next(item[1] for item in existing_l1_list if item[0] == parent_selection)
            
            level_choice = st.selectbox("組織層級", ["L2 - 二級部門 / 課室", "L1 - 頂級大部門", "L3 - 三級組別"])
            name_zh = st.text_input("部門繁體中文名稱 *", placeholder="例如: 工程部")
            name_vi = st.text_input("部門越文名稱", placeholder="Ví dụ: Phòng Kỹ thuật")
            
            st.markdown("---")
            st.markdown("#### 🧩 勾選並掛載此部門可操作的業務模組：")

            selected_department_modules = []
            for cat_name, mod_list in ALL_AVAILABLE_MODULES.items():
                with st.expander(f"{cat_name} （包含 {len(mod_list)} 項功能）", expanded=False):
                    for mod_name, mod_key in mod_list:
                        if st.checkbox(f"**{mod_name}**", key=f"chk_add_{mod_key}"):
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
        st.markdown("##### 📋 現有部門清單與模組即時調整")
        if conn_status:
            try:
                df_existing = pd.read_sql("SELECT dept_code, dept_name_zh, level_depth FROM sys_departments WHERE is_active = TRUE", con=active_engine)
                if not df_existing.empty:
                    dept_options = {f"[{row['level_depth']}] {row['dept_name_zh']}": row["dept_code"] for _, row in df_existing.iterrows()}
                    selected_target = st.selectbox("🎯 選擇要調整的部門", list(dept_options.keys()), key="manage_dept_select")
                    target_code = dept_options[selected_target]

                    df_current_mods = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :code"), con=active_engine, params={"code": target_code})
                    current_assigned = df_current_mods["module_name"].tolist() if not df_current_mods.empty else []

                    st.markdown(f"**📌 目前已掛載的模組 ({len(current_assigned)} 個)：**")
                    
                    with st.form(f"manage_mods_form_{target_code}"):
                        new_checked_modules = []
                        for cat_name, mod_list in ALL_AVAILABLE_MODULES.items():
                            st.markdown(f"**{cat_name}**")
                            for mod_name, mod_key in mod_list:
                                is_default = mod_name in current_assigned
                                if st.checkbox(mod_name, value=is_default, key=f"manage_chk_{target_code}_{mod_key}"):
                                    new_checked_modules.append(mod_name)
                            st.markdown("")

                        update_btn = st.form_submit_button("💾 儲存該部門的模組掛載異動", type="primary", use_container_width=True)
                        if update_btn:
                            with active_engine.begin() as conn:
                                conn.execute(text("DELETE FROM sys_department_modules WHERE dept_code = :code"), {"code": target_code})
                                for m_name in new_checked_modules:
                                    conn.execute(text("INSERT INTO sys_department_modules (dept_code, module_name) VALUES (:code, :m_name)"), {"code": target_code, "m_name": m_name})
                            st.success("🎉 該部門的模組掛載已成功更新！")
                            st.rerun()

                    st.markdown("---")
                    if st.button("🗑️ 永久裁撤/停用此部門", type="secondary"):
                        with active_engine.begin() as conn:
                            conn.execute(text("UPDATE sys_departments SET is_active = FALSE WHERE dept_code = :code"), {"code": target_code})
                        st.warning("⚠️ 部門已成功停用！")
                        st.rerun()
            except Exception as e:
                st.error(f"讀取失敗: {e}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
