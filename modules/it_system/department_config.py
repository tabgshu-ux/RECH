# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構 L1~L4 動態配置、左側選單聯動與「跨群組彈性業務模組掛載」中心
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_dept_tables(engine):
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 1. 組織部門表（支援 L1~L4 階層與停用狀態，保護合約與歷史資料）
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
                # 2. 部門模組動態掛載對應表
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
    st.markdown("### 🏢 公司組織架構與 L1~L4 彈性模組掛載中心")
    st.caption("100% 鬆耦合架構：支援 L1～L4 動態擴編部門，並可跨部門自由勾選各功能群組（如行政兼辦總務），左側選單即時雙向聯動。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_dept_tables(engine)

    # 確保預設有基本部門與模組對應
    try:
        with engine.begin() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM sys_departments")).scalar()
            if cnt == 0:
                conn.execute(text("""
                    INSERT INTO sys_departments (dept_code, dept_name, parent_dept, level_tier, is_active) VALUES 
                    ('EXEC', '總經理室總覽', '總公司', 'L1', TRUE),
                    ('ENG', '工程部總覽', '總公司', 'L1', TRUE),
                    ('MGMT', '管理部總覽', '總公司', 'L1', TRUE),
                    ('ADMIN', '行政課', '管理部總覽', 'L2', TRUE),
                    ('GA', '總務課', '管理部總覽', 'L2', TRUE),
                    ('PROD', '生產部總覽', '總公司', 'L1', TRUE),
                    ('FIN', '財務與稅務管理', '總公司', 'L1', TRUE)
                    ON CONFLICT (dept_code) DO NOTHING;
                """))
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO sys_department_modules (dept_name, mounted_features)
                VALUES 
                ('總經理室總覽', 'feat_mgmt_supervisor,feat_announcements'),
                ('管理部總覽', 'feat_mgmt_supervisor,feat_announcements,feat_hr_employee,feat_hr_attendance,feat_hr_payroll,feat_ga'),
                ('行政課', 'feat_hr_employee,feat_hr_attendance,feat_hr_payroll'),
                ('總務課', 'feat_ga,feat_ga_expat,feat_ga_ehs,feat_ga_canteen,feat_ga_mro'),
                ('工程部總覽', 'feat_site_log'),
                ('生產部總覽', 'feat_panel_build,feat_material'),
                ('財務與稅務管理', 'feat_fi')
                ON CONFLICT (dept_name) DO NOTHING;
            """))
    except Exception:
        pass

    # 三大核心分頁
    tab_tree, tab_mount, tab_add = st.tabs(["🌳 現有組織樹與狀態管理", "⚙️ 跨群組彈性模組掛載", "➕ 新增擴編 L1~L4 部門"])

    # ==========================================
    # 分頁一：組織樹檢視與狀態控制（隱藏/啟用）
    # ==========================================
    with tab_tree:
        st.markdown("#### 🌳 L1～L4 企業組織樹狀架構與左側聯動狀態")
        st.info("💡 提示：將部門設為「隱藏/停用」時，左側導覽列將即時移除該按鈕，但資料庫中所有歷史合約、考勤與憑證資料皆會完整保留。")

        try:
            with engine.connect() as conn:
                depts = conn.execute(text("SELECT id, dept_code, dept_name, parent_dept, level_tier, is_active FROM sys_departments ORDER BY id")).fetchall()
        except Exception:
            depts = []

        for d in depts:
            dept_id, d_code, d_name, parent, d_tier, is_active = d
            status_badge = "🟢 顯示中 (Active)" if is_active else "🔴 已隱藏 (Disabled)"
            
            with st.expander(f"[{d_tier}] {d_name} (上級: {parent}) — {status_badge}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**組織層級:** {d_tier} | **上級部門:** {parent} | **狀態:** {'正常顯示' if is_active else '已隱藏（合約資料保留）'}")
                with col2:
                    toggle_label = "🔴 隱藏 / 停用" if is_active else "🟢 恢復顯示"
                    if st.button(toggle_label, key=f"toggle_tree_dept_{dept_id}", use_container_width=True):
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE sys_departments SET is_active = :act WHERE id = :did"), {"act": not is_active, "did": dept_id})
                            st.success(f"🎉 部門 [{d_name}] 狀態已更新！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"狀態更新失敗: {e}")

    # ==========================================
    # 分頁二：跨群組彈性業務模組動態掛載
    # ==========================================
    with tab_mount:
        st.markdown("#### ⚙️ 跨部門群組彈性業務模組掛載中心")
        st.caption("💡 支援小公司彈性兼任：您可以選擇任意部門（例如：行政課），並跨群組勾選總務或其他部門的專屬功能來進行掛載。")

        try:
            with engine.connect() as conn:
                dept_rows = conn.execute(text("SELECT dept_name, level_tier FROM sys_departments WHERE is_active = TRUE ORDER BY id")).fetchall()
                dept_names = [r[0] for r in dept_rows]
        except Exception:
            dept_names = ["管理部總覽", "行政課", "總務課"]

        if not dept_names:
            dept_names = ["管理部總覽"]

        selected_dept = st.selectbox("🎯 選擇要掛載模組的目標部門（可任意指定大小部門）", dept_names, key="mount_dept_select")

        # 清楚標明功能所屬群組，方便跨部門彈性兼任勾選
        categorized_features = {
            "🏢 【管理與公告群組】": {
                "管理部總覽 / 戰情室": "feat_mgmt_supervisor",
                "公司公告佈告欄": "feat_announcements"
            },
            "📁 【行政人事群組】": {
                "人事行政課 - 員工檔案與履約管理": "feat_hr_employee",
                "人事行政課 - 考勤與打卡紀錄": "feat_hr_attendance",
                "人事行政課 - 薪資計算與 BHXH 保險": "feat_hr_payroll",
                "外勤油費與外出補助津貼管理": "feat_allowance"
            },
            "📂 【總務後勤群組】": {
                "總務採購課 - 採購單與應付帳款 (AP)": "feat_ga",
                "🛂 總務後勤 - 台幹證件與生活支援 (Expat Support)": "feat_ga_expat",
                "🧯 總務後勤 - 廠務設施與 EHS 環安衛合規": "feat_ga_ehs",
                "🍲 總務後勤 - 越籍員工食堂團膳與門禁秩序": "feat_ga_canteen",
                "🏛️ 總務後勤 - MRO 採購與政府公關 (PR)": "feat_ga_mro"
            },
            "💰 【財務會計群組】": {
                "財務會計課 - 應收帳款管理 (AR) 與財報": "feat_fi"
            },
            "🛠️ 【工程與生產群組】": {
                "工程部 - 工地日報與巡檢": "feat_site_log",
                "生產部 - 組裝與看板": "feat_panel_build",
                "倉庫管理": "feat_material",
                "簽核中心": "feat_my_approvals"
            }
        }

        # 讀取該部門目前已掛載的模組
        mounted_list = []
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d"), {"d": selected_dept}).fetchone()
                if res and res[0]:
                    mounted_list = res[0].split(",")
        except Exception:
            pass

        with st.form("dept_modules_mount_form"):
            new_mounted = []
            
            for group_name, features in categorized_features.items():
                st.markdown(f"**{group_name}**")
                for label, feat_id in features.items():
                    is_checked = st.checkbox(label, value=(feat_id in mounted_list), key=f"chk_mount_{selected_dept}_{feat_id}")
                    if is_checked:
                        new_mounted.append(feat_id)
                st.markdown("---")

            submitted_mount = st.form_submit_button("💾 儲存並即時生效部門模組掛載", type="primary", use_container_width=True)
            if submitted_mount:
                try:
                    mounted_str = ",".join(new_mounted)
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_department_modules (dept_name, mounted_features, updated_at)
                            VALUES (:dname, :feats, CURRENT_TIMESTAMP)
                            ON CONFLICT (dept_name) 
                            DO UPDATE SET mounted_features = :feats, updated_at = CURRENT_TIMESTAMP
                        """), {"dname": selected_dept, "feats": mounted_str})
                    st.success(f"🎉 [{selected_dept}] 的跨群組業務模組掛載已成功更新！")
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存掛載失敗: {e}")

    # ==========================================
    # 分頁三：新增擴編 L1~L4 部門（支援上下級指定）
    # ==========================================
    with tab_add:
        st.markdown("#### ➕ 新增擴編組織部門 (支援 L1～L4 層級與上級指定)")
        st.caption("在此新增部門（例如在管理部底下新增 L2 行政課或 L3 總務組），新增後將自動同步至左側導覽列。")

        try:
            with engine.connect() as conn:
                parent_rows = conn.execute(text("SELECT dept_name FROM sys_departments WHERE is_active = TRUE")).fetchall()
                parent_options = ["總公司"] + [r[0] for r in parent_rows]
        except Exception:
            parent_options = ["總公司", "管理部總覽"]

        with st.form("add_new_dept_form_full"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_code = st.text_input("部門英文代碼 (例如: ADMIN_SUB, GA_SUB)", placeholder="請輸入唯一代碼")
                new_name = st.text_input("部門正式名稱 (例如: 行政課 / 總務課)", placeholder="請輸入部門名稱")
            with col_b:
                parent_opt = st.selectbox("上級所屬部門", parent_options)
                tier_opt = st.selectbox("組織層級 (Tier)", ["L1 (一級大部門)", "L2 (二級子部門/課)", "L3 (三級分組)", "L4 (四級小組)"])

            submitted_create = st.form_submit_button("🚀 確認新增擴編部門並同步左側選單", type="primary", use_container_width=True)

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
                            conn.execute(text("""
                                INSERT INTO sys_department_modules (dept_name, mounted_features)
                                VALUES (:dname, 'feat_mgmt_supervisor,feat_announcements')
                                ON CONFLICT (dept_name) DO NOTHING;
                            """), {"dname": new_name.strip()})

                        st.success(f"🎉 成功新增擴編部門：[{tier_code}] {new_name.strip()}（上級：{parent_opt}）！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 新增失敗: {e}")
                else:
                    st.warning("⚠️ 請完整填寫部門代碼與名稱。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
