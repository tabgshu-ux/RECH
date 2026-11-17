# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構 L1~L4 動態配置與各部門業務模組勾選掛載中心
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
    st.caption("在此動態維護公司組織架構與部門模組掛載。勾選後將即時生效於各部門選單。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_dept_tables(engine)

    dept_options = [
        "[L1] 總經理室 (Executive Office)",
        "[L1] 管理部 (Management Dept)",
        "[L1] 工程與設計管理中心",
        "[L1] 生產製造與倉庫管理",
        "[L1] 財務與稅務管理"
    ]
    
    selected_dept = st.selectbox("🎯 選擇要調整與掛載模組的部門", dept_options, index=1)

    st.markdown("---")
    st.markdown("#### ⚙️ 勾選並掛載此部門可操作的業務模組：")

    # 🌟 這裡已完整納入您剛剛要求的 4 大總務後勤模組
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

    with st.form("dept_modules_form"):
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
                st.success("🎉 部門模組動態掛載已成功更新！")
                st.rerun()
            except Exception as e:
                st.error(f"儲存掛載失敗: {e}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
