# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構 L1~L4 動態配置與左側選單即時聯動中心（嚴格禁止刪除、改採「停用」機制）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_dept_tables(engine):
    """初始化部門組織與模組掛載資料表（支援狀態停用欄位，防止系統錯亂）"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 1. 組織部門表（加入 is_active 狀態，只允許停用不允許直接刪除）
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
                # 2. 部門模組掛載對應表
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
    st.markdown("### 🏢 公司組織架構與 L1~L4 動態配置中心")
    st.caption("左側選單即時聯動：在此新增擴編、勾選掛載模組或將暫不使用的部門設為「停用」（避免刪除造成系統資料錯亂）。")

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
                    ('EXEC', '總經理室 (Executive Office)', '總公司', 'L1', TRUE),
                    ('MGMT', '管理部 (Management Dept)', '總公司', 'L1', TRUE),
                    ('ENG', '工程與設計管理中心', '總公司', 'L1', TRUE),
                    ('PROD', '生產製造與倉庫管理', '總公司', 'L1', TRUE),
                    ('FIN', '財務與稅務管理', '總公司', 'L1', TRUE)
                    ON CONFLICT (dept_code) DO NOTHING;
                """))
        # 同步確保預設模組對應存在
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO sys_department_modules (dept_name, mounted_features)
                VALUES 
                ('總經理室 (Executive Office)', 'feat_mgmt_supervisor,feat_announcements'),
                ('管理部 (Management Dept)', 'feat_mgmt_supervisor,feat_announcements,feat_hr_employee,feat_hr_attendance,feat_hr_payroll,feat_ga,feat_ga_expat,feat_ga_ehs,feat_ga_canteen,feat_ga_mro,feat_fi'),
                ('工程與設計管理中心', 'feat_site_log'),
                ('生產製造與倉庫管理', 'feat_panel_build,feat_material'),
                ('財務與稅務管理', 'feat_fi')
                ON CONFLICT (dept_name) DO NOTHING;
            """))
    except Exception:
        pass

    # 建立分頁：1. 現有組織樹與模組掛載管理 vs 2. 新增擴編 L1~L4 部門
    tab_manage, tab_add = st.tabs(["🌳 現有組織樹與模組掛載管理", "➕ 新增擴編 L1~L4 部門"])

    # ==========================================
    # 分頁一：現有組織樹、狀態切換（停用/啟用）與模組掛載
    # ==========================================
    with tab_manage:
        st.markdown("#### 📋 現有部門清單與左側選單聯動管理")
        st.caption("💡 提示：為保護會計、考勤與簽核歷史資料的完整性，系統採用**「停用 (Disable)」**機制取代刪除，停用後左側導覽樹將自動隱藏該部門。")

        try:
            with engine.connect() as conn:
                depts = conn.execute(text("SELECT id, dept_code, dept_name, level_tier, is_active FROM sys_departments ORDER BY id")).fetchall()
        except Exception:
            depts = []

        for d in depts:
            dept_id, d_code, d_name, d_tier, is_active = d
            status_badge = "🟢 啟用中 (Active)" if is_active else "🔴 已停用 (Disabled)"
            
            with st.expander(f"[{d_tier}] {d_name} (代碼: {d_code}) — {status_badge}"):
                col_info, col_action = st.columns([3, 1])
                with col_info:
                    st.markdown(f"**所屬層級:** {d_tier} | **狀態:** {'正常顯示於左側選單' if is_active else '已從左側選單隱藏'}")
                with col_action:
                    # 停用 / 啟用切換按鈕
                    toggle_label = "🔴 設為停用" if is_active else "🟢 恢復啟用"
                    if st.button(toggle_label, key=f"toggle_dept_{dept_id}", use_container_width=True):
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE sys_departments SET is_active = :act WHERE id = :did"), {"act": not is_active, "did": dept_id})
                            st.success(f"🎉 部門 [{d_name}] 狀態已更新！左側選單已同步聯動。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"狀態更新失敗: {e}")

                st.markdown("---")
                st.markdown("##### ⚙️ 該部門可操作之業務模組掛載設定：")

                # 可勾選的模組清單
                available_features = {
                    "管理部總覽 / 戰情室": "feat_mgmt_supervisor",
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
                        res = conn.execute(text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d"), {"d": d_name}).fetchone()
                        if res and res[0]:
                            mounted_list = res[0].split(",")
                except Exception:
                    pass

                with st.form(f"form_dept_{dept_id}"):
                    new_mounted = []
                    for label, feat_id in available_features.items():
                        is_chk = st.checkbox(label, value=(feat_id in mounted_list), key=f"chk_{dept_id}_{feat_id}")
                        if is_chk:
                            new_mounted.append(feat_id)

                    submitted_mod = st.form_submit_button(f"💾 儲存 [{d_name}] 模組掛載", type="primary")
                    if submitted_mod:
                        try:
                            mounted_str = ",".join(new_mounted)
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO sys_department_modules (dept_name, mounted_features, updated_at)
                                    VALUES (:dname, :feats, CURRENT_TIMESTAMP)
                                    ON CONFLICT (dept_name) 
                                    DO UPDATE SET mounted_features = :feats, updated_at = CURRENT_TIMESTAMP
                                """), {"dname": d_name, "feats": mounted_str})
                            st.success(f"🎉 [{d_name}] 模組掛載已成功更新！左側選單已即時聯動。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"儲存失敗: {e}")

    # ==========================================
    # 分頁二：新增擴編 L1~L4 部門（自動聯動左側選單）
    # ==========================================
    with tab_add:
        st.markdown("#### ➕ 新增擴編組織部門 (L1～L4 動態擴充)")
        st.caption("新增的部門將直接寫入資料庫，並自動與左側組織樹導覽進行雙向聯動顯示。")

        with st.form("add_new_dept_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_code = st.text_input("部門英文代碼 (例如: ESG, RD)", placeholder="請輸入唯一代碼")
                new_name = st.text_input("部門正式名稱 (例如: ESG 永續發展室)", placeholder="請輸入部門名稱")
            with col_b:
                parent_opt = st.selectbox("上級所屬部門", ["總公司", "管理部 (Management Dept)", "工程與設計管理中心", "生產製造與倉庫管理"])
                tier_opt = st.selectbox("組織層級 (Tier)", ["L1 (一級部門)", "L2 (二級部門)", "L3 (課級部門)", "L4 (組級部門)"])

            submitted_create = st.form_submit_button("🚀 確認新增擴編部門並聯動左側選單", type="primary", use_container_width=True)

            if submitted_create:
                if new_code and new_name:
                    try:
                        tier_code = tier_opt.split(" ")[0]
                        with engine.begin() as conn:
                            # 1. 寫入部門表
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
                            # 2. 同步初始化預設模組掛載
                            conn.execute(text("""
                                INSERT INTO sys_department_modules (dept_name, mounted_features)
                                VALUES (:dname, 'feat_mgmt_supervisor,feat_announcements')
                                ON CONFLICT (dept_name) DO NOTHING;
                            """), {"dname": new_name.strip()})

                        st.success(f"🎉 成功新增擴編部門：[{tier_code}] {new_name.strip()}！左側組織樹與選單已自動聯動。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 新增失敗: {e}")
                else:
                    st.warning("⚠️ 請完整填寫部門代碼與名稱。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
