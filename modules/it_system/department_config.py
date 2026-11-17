# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構 L1~L4 動態配置與跨群組彈性業務模組掛載中心（智慧相容現有資料庫結構）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_dept_tables(engine):
    """安全初始化資料庫，自動檢測現有欄位並補齊所需結構"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 建立基本表（若不存在）
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_departments (
                        id SERIAL PRIMARY KEY,
                        dept_code VARCHAR(50) UNIQUE NOT NULL,
                        name VARCHAR(150),
                        dept_name VARCHAR(150),
                        parent_dept VARCHAR(150) DEFAULT '總公司',
                        level_tier VARCHAR(10) DEFAULT 'L1',
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                
                # 自動補齊可能缺少的欄位，防止任何 UndefinedColumn 錯誤
                for col_sql in [
                    "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS dept_code VARCHAR(50);",
                    "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS name VARCHAR(150);",
                    "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS dept_name VARCHAR(150);",
                    "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS parent_dept VARCHAR(150) DEFAULT '總公司';",
                    "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS level_tier VARCHAR(10) DEFAULT 'L1';",
                    "ALTER TABLE sys_departments ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;"
                ]:
                    try:
                        conn.execute(text(col_sql))
                    except Exception:
                        pass

                # 模組掛載表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        dept_name VARCHAR(150) PRIMARY KEY,
                        mounted_features TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"⚠️ 初始化發生異常: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏢 公司組織架構與 L1~L4 彈性模組掛載中心")
    st.caption("支援 L1～L4 動態擴編部門，並可跨部門自由勾選各功能群組，左側選單即時雙向聯動。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_dept_tables(engine)

    tab_tree, tab_mount, tab_add = st.tabs(["🌳 現有組織樹與狀態管理", "⚙️ 跨群組彈性模組掛載", "➕ 新增擴編 L1~L4 部門"])

    # ==========================================
    # 分頁一：組織樹檢視與狀態控制
    # ==========================================
    with tab_tree:
        st.markdown("#### 🌳 企業組織樹狀架構與左側聯動狀態")
        try:
            with engine.connect() as conn:
                # 同時相容 dept_name 或 name 欄位
                depts = conn.execute(text("SELECT id, dept_code, COALESCE(dept_name, name, '未命名部門'), parent_dept, level_tier, is_active FROM sys_departments ORDER BY id")).fetchall()
        except Exception:
            depts = []

        if depts:
            for d in depts:
                dept_id, d_code, d_name, parent, d_tier, is_active = d
                is_active_val = True if is_active is None else is_active
                status_badge = "🟢 顯示中 (Active)" if is_active_val else "🔴 已隱藏 (Disabled)"
                
                with st.expander(f"[{d_tier or 'L1'}] {d_name} (代碼: {d_code}) — {status_badge}"):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**組織層級:** {d_tier or 'L1'} | **上級部門:** {parent or '總公司'}")
                    with col2:
                        toggle_label = "🔴 隱藏 / 停用" if is_active_val else "🟢 恢復顯示"
                        if st.button(toggle_label, key=f"toggle_tree_dept_{dept_id}", use_container_width=True):
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("UPDATE sys_departments SET is_active = :act WHERE id = :did"), {"act": not is_active_val, "did": dept_id})
                                st.success(f"🎉 部門狀態已更新！")
                                st.rerun()
                            except Exception as e:
                                st.error(f"更新失敗: {e}")
        else:
            st.info("💡 目前尚無部門資料，請至右側「新增擴編部門」建立。")

    # ==========================================
    # 分頁二：跨群組彈性業務模組動態掛載
    # ==========================================
    with tab_mount:
        st.markdown("#### ⚙️ 跨部門群組彈性業務模組掛載中心")
        try:
            with engine.connect() as conn:
                dept_rows = conn.execute(text("SELECT COALESCE(dept_name, name) FROM sys_departments WHERE is_active = TRUE OR is_active IS NULL ORDER BY id")).fetchall()
                dept_names = [r[0] for r in dept_rows if r[0]]
        except Exception:
            dept_names = []

        if not dept_names:
            dept_names = ["管理部總覽", "工程部總覽", "總經理室總覽"]

        selected_dept = st.selectbox("🎯 選擇要掛載模組的目標部門", dept_names, key="mount_dept_select")

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
                    st.success(f"🎉 [{selected_dept}] 的業務模組掛載已成功更新！")
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

    # ==========================================
    # 分頁三：新增擴編 L1~L4 部門
    # ==========================================
    with tab_add:
        st.markdown("#### ➕ 新增擴編組織部門 (支援 L1～L4 層級)")
        try:
            with engine.connect() as conn:
                parent_rows = conn.execute(text("SELECT COALESCE(dept_name, name) FROM sys_departments")).fetchall()
                parent_options = ["總公司"] + [r[0] for r in parent_rows if r[0]]
        except Exception:
            parent_options = ["總公司"]

        with st.form("add_new_dept_form_full"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_code = st.text_input("部門英文代碼 (例如: ADMIN, GA)", placeholder="請輸入唯一代碼")
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
                            # 同時寫入 dept_name 與 name 欄位，確保絕對相容您現有的 Supabase 表結構
                            conn.execute(text("""
                                INSERT INTO sys_departments (dept_code, dept_name, name, parent_dept, level_tier, is_active, updated_at)
                                VALUES (:code, :name, :name, :parent, :tier, TRUE, CURRENT_TIMESTAMP)
                                ON CONFLICT (dept_code) DO UPDATE 
                                SET dept_name = :name, name = :name, parent_dept = :parent, level_tier = :tier, is_active = TRUE, updated_at = CURRENT_TIMESTAMP
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

                        st.success(f"🎉 成功新增擴編部門：[{tier_code}] {new_name.strip()}！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 新增失敗: {e}")
                else:
                    st.warning("⚠️ 請完整填寫部門代碼與名稱。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
