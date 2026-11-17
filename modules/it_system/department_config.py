# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構 L1~L4 動態配置與左側選單即時聯動中心（保留合約歷史、僅以狀態控制顯示）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_dept_tables(engine):
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_departments (
                        id SERIAL PRIMARY KEY,
                        dept_code VARCHAR(50) UNIQUE NOT NULL,
                        dept_name VARCHAR(150) NOT NULL,
                        parent_dept VARCHAR(150) DEFAULT '總公司',
                        level_tier VARCHAR(10) DEFAULT 'L1',
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        dept_name VARCHAR(150) PRIMARY KEY,
                        mounted_features TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"⚠️ 初始化組織架構資料表發生異常: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏢 公司組織架構與左側選單動態聯動中心")
    st.caption("在此新增或停用部門。停用後左側導覽列將即時移除該部門按鈕，但底層合約與歷史資料完整保留不刪除。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_dept_tables(engine)

    # 確保預設有基本部門
    try:
        with engine.begin() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM sys_departments")).scalar()
            if cnt == 0:
                conn.execute(text("""
                    INSERT INTO sys_departments (dept_code, dept_name, parent_dept, level_tier, is_active) VALUES 
                    ('EXEC', '總經理室總覽', '總公司', 'L1', TRUE),
                    ('ENG', '工程部總覽', '總公司', 'L1', TRUE),
                    ('MGMT', '管理部總覽', '總公司', 'L1', TRUE),
                    ('PROD', '生產部總覽', '總公司', 'L1', TRUE),
                    ('WAREHOUSE', '倉庫管理', '總公司', 'L1', TRUE),
                    ('APPROVAL', '簽核中心', '總公司', 'L1', TRUE)
                    ON CONFLICT (dept_code) DO NOTHING;
                """))
    except Exception:
        pass

    tab_manage, tab_add = st.tabs(["📋 現有部門狀態與左側聯動管理", "➕ 新增擴編部門"])

    with tab_manage:
        st.markdown("#### 🔄 部門顯示與隱藏（停用）控制")
        try:
            with engine.connect() as conn:
                depts = conn.execute(text("SELECT id, dept_code, dept_name, level_tier, is_active FROM sys_departments ORDER BY id")).fetchall()
        except Exception:
            depts = []

        for d in depts:
            dept_id, d_code, d_name, d_tier, is_active = d
            status_text = "🟢 顯示中 (Active - 左側選單可見)" if is_active else "🔴 已隱藏 (Disabled - 左側選單已移除，合約資料保留)"
            
            with st.expander(f"[{d_tier}] {d_name} (代碼: {d_code}) — {status_text}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**部門名稱:** {d_name} | **狀態:** {'正常顯示於左側導覽' if is_active else '已從左側導覽移除（歷史合約安全保留）'}")
                with col2:
                    toggle_label = "🔴 隱藏 / 停用" if is_active else "🟢 恢復顯示"
                    if st.button(toggle_label, key=f"toggle_dept_{dept_id}", use_container_width=True):
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE sys_departments SET is_active = :act WHERE id = :did"), {"act": not is_active, "did": dept_id})
                            st.success(f"🎉 部門 [{d_name}] 狀態已更新！左側導覽選單已即時聯動。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"更新失敗: {e}")

    with tab_add:
        st.markdown("#### ➕ 新增擴編部門（自動同步至左側導覽）")
        with st.form("add_new_dept_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_code = st.text_input("部門英文代碼 (例如: ESG, QA)", placeholder="請輸入代碼")
                new_name = st.text_input("部門正式名稱 (將顯示於左側選單)", placeholder="例如: 品質保證部總覽")
            with col_b:
                parent_opt = st.selectbox("上級所屬部門", ["總公司", "管理部", "工程部", "生產部"])
                tier_opt = st.selectbox("組織層級", ["L1 (一級部門)", "L2 (二級部門)"])

            submitted_create = st.form_submit_button("🚀 確認新增部門並即時更新左側選單", type="primary", use_container_width=True)

            if submitted_create:
                if new_code and new_name:
                    try:
                        tier_code = tier_opt.split(" ")[0]
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO sys_departments (dept_code, dept_name, parent_dept, level_tier, is_active, updated_at)
                                VALUES (:code, :name, :parent, :tier, TRUE, CURRENT_TIMESTAMP)
                                ON CONFLICT (dept_code) DO UPDATE 
                                SET dept_name = :name, parent_dept = :parent, level_tier = :tier, is_active = TRUE, updated_at = CURRENT_TIMESTAMP
                            """), {
                                "code": new_code.upper().strip(),
                                "name": new_name.strip(),
                                "parent": parent_opt,
                                "tier": tier_code
                            })
                        st.success(f"🎉 成功新增部門：[{new_name.strip()}]！左側導覽選單已即時出現該按鈕。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 新增失敗: {e}")
                else:
                    st.warning("⚠️ 請完整填寫代碼與名稱。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
