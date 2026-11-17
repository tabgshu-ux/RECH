# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構 L1~L4 動態配置與各部門業務模組勾選掛載中心（維持手機優先的 Tab 分頁設計）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_dept_tables(engine):
    if engine:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        dept_name VARCHAR(150) PRIMARY KEY,
                        mounted_features TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"初始化部門模組對應表失敗: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏢 公司組織架構與 L1~L4 動態配置中心")
    st.caption("在此動態維護公司組織架構與部門模組掛載。點擊下方部門 Tab 分頁即可切換並勾選掛載。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_dept_tables(engine)

    # 1. 將下拉式選單改回手機與電腦皆好用的 Tab 分頁按鈕列
    dept_tabs_meta = [
        {"id": "exec", "name": "🏢 總經理室 (Executive Office)", "db_name": "[L1] 總經理室 (Executive Office)"},
        {"id": "mgmt", "name": "👥 管理部 (Management Dept)", "db_name": "[L1] 管理部 (Management Dept)"},
        {"id": "eng", "name": "⚙️ 工程與設計管理中心", "db_name": "[L1] 工程與設計管理中心"},
        {"id": "prod", "name": "🏭 生產製造與倉庫管理", "db_name": "[L1] 生產製造與倉庫管理"},
        {"id": "fin", "name": "💰 財務與稅務管理", "db_name": "[L1] 財務與稅務管理"}
    ]

    if 'active_dept_tab' not in st.session_state:
        st.session_state['active_dept_tab'] = 'mgmt'

    cols = st.columns(len(dept_tabs_meta))
    for idx, tab_info in enumerate(dept_tabs_meta):
        with cols[idx]:
            is_active = (st.session_state['active_dept_tab'] == tab_info['id'])
            if st.button(tab_info['name'], use_container_width=True, type="primary" if is_active else "secondary"):
                st.session_state['active_dept_tab'] = tab_info['id']
                st.rerun()

    # 取得當前選中的部門資料庫名稱
    current_dept_info = next((t for t in dept_tabs_meta if t['id'] == st.session_state['active_dept_tab']), dept_tabs_meta[1])
    selected_dept = current_dept_info['db_name']

    st.markdown("---")
    st.markdown(f"#### ⚙️ 正在設定部門：`{selected_dept}` 的模組掛載清單")

    # 定義各部門可勾選的功能清單（包含總務後勤 4 大新模組）
    management_features = {
        "管理部總覽": "feat_mgmt_supervisor",
        "公司公告佈告欄": "feat_announcements",
        "人事行政課 - 員工檔案與履約管理": "feat_hr_employee",
        "人事行政課 - 考勤與打卡紀錄": "feat_hr_attendance",
        "人事行政課 - 薪資計算與 BHXH 保險": "feat_hr_payroll",
        "外勤油費與外出補助津貼管理": "feat_allowance",
        "總務採購課 - 採購單與應付帳款 (AP)": "feat_ga",
        "🛂 總務後勤 - 台幹證件與生活支援 (Expat Support)": "feat_ga_expat",
        "🧯 總務後勤 - 廠務設施與 EHS 環安衛合規": "feat_ga_ehs",
        "🍲 總務後勤 - 越籍員工食堂團膳與門禁秩序": "feat_ga_canteen",
        "🏛️ 總務後勤 - MRO 採購與政府公關 (PR)": "feat_ga_mro",
        "財務會計課 - 應收帳款管理 (AR) 與財報": "feat_fi"
    }

    # 讀取現有掛載
    mounted_list = []
    try:
        with engine.connect() as conn:
            res = conn.execute(text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d"), {"d": selected_dept}).fetchone()
            if res and res[0]:
                mounted_list = res[0].split(",")
    except Exception:
        pass

    if not mounted_list:
        mounted_list = ["feat_mgmt_supervisor", "feat_announcements", "feat_ga"]

    with st.form(f"dept_modules_form_{current_dept_info['id']}"):
        new_mounted = []
        for label, feat_id in management_features.items():
            is_checked = st.checkbox(label, value=(feat_id in mounted_list))
            if is_checked:
                new_mounted.append(feat_id)

        submitted = st.form_submit_button("💾 儲存並即時生效部門模組掛載", type="primary", use_container_width=True)
        if submitted:
            try:
                mounted_str = ",".join(new_mounted)
                with engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO sys_department_modules (dept_name, mounted_features, updated_at)
                        VALUES (:dept, :feats, CURRENT_TIMESTAMP)
                        ON CONFLICT (dept_name) 
                        DO UPDATE SET mounted_features = :feats, updated_at = CURRENT_TIMESTAMP
                    """), {"dept": selected_dept, "feats": mounted_str})
                st.success(f"🎉 [{selected_dept}] 的模組動態掛載已成功更新！")
                st.rerun()
            except Exception as e:
                st.error(f"儲存掛載失敗: {e}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
