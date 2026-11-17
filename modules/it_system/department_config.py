# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：公司組織架構 L1~L4 動態配置中心（支援資料庫動態讀取、自由新增擴編部門與模組掛載）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def init_dept_tables(engine):
    """自動初始化組織部門與模組掛載資料表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 1. 部門清單資料表（支援動態新增 L1~L4 組織）
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_departments (
                        id SERIAL PRIMARY KEY,
                        dept_code VARCHAR(50) UNIQUE NOT NULL,
                        dept_name VARCHAR(150) NOT NULL,
                        parent_dept VARCHAR(150) DEFAULT '總公司',
                        level_tier VARCHAR(10) DEFAULT 'L1',
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # 2. 部門與業務模組掛載對應表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        dept_name VARCHAR(150) PRIMARY KEY,
                        mounted_features TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"⚠️ 初始化動態組織架構資料表發生異常: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🏢 公司組織架構與 L1~L4 動態配置中心")
    st.caption("100% 動態資料庫驅動：支援未來公司擴編時自由新增部門、調整組織樹分層，並即時勾選掛載各部門專屬業務模組。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎。")
        return

    init_dept_tables(engine)

    # 確保預設有基本部門，若資料庫為空則自動植入
    try:
        with engine.begin() as conn:
            cnt = conn.execute(text("SELECT COUNT(*) FROM sys_departments")).scalar()
            if cnt == 0:
                conn.execute(text("""
                    INSERT INTO sys_departments (dept_code, dept_name, parent_dept, level_tier) VALUES 
                    ('EXEC', '總經理室 (Executive Office)', '總公司', 'L1'),
                    ('MGMT', '管理部 (Management Dept)', '總公司', 'L1'),
                    ('ENG', '工程與設計管理中心', '總公司', 'L1'),
                    ('PROD', '生產製造與倉庫管理', '總公司', 'L1'),
                    ('FIN', '財務與稅務管理', '總公司', 'L1')
                    ON CONFLICT (dept_code) DO NOTHING;
                """))
    except Exception:
        pass

    # 建立頂部切換檢視：1. 動態調整部門模組掛載 vs 2. 新增擴編 L1~L4 部門
    sub_mode = st.radio("選擇操作模式", ["⚙️ 現有部門模組掛載調整", "➕ 新增擴編 L1~L4 部門與組織樹"], horizontal=True)
    st.markdown("---")

    # ==========================================
    # 模式一：動態讀取資料庫部門並調整模組掛載
    # ==========================================
    if sub_mode == "⚙️ 現有部門模組掛載調整":
        # 從資料庫動態撈取所有部門清單（絕對不寫死）
        try:
            with engine.connect() as conn:
                dept_rows = conn.execute(text("SELECT dept_name, level_tier FROM sys_departments ORDER BY id")).fetchall()
                dept_list = [f"[{r[1]}] {r[0]}" for r in dept_rows]
        except Exception:
            dept_list = ["[L1] 管理部 (Management Dept)", "[L1] 總經理室 (Executive Office)"]

        if not dept_list:
            dept_list = ["[L1] 管理部 (Management Dept)"]

        selected_dept_label = st.selectbox("🎯 選擇要調整模組掛載的部門", dept_list)
        # 提取純部門名稱
        selected_dept = selected_dept_label.split("] ")[1] if "] " in selected_dept_label else dept_list[0]

        st.markdown(f"#### ⚙️ 正在配置部門：`{selected_dept}` 的業務模組掛載清單")

        # 定義系統所有可供勾選的模組清單（包含新加入的總務後勤 4 大模組）
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

        # 從資料庫讀取該部門目前已掛載的模組
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
            for label, feat_id in available_features.items():
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

    # ==========================================
    # 模式二：自行新增擴編 L1~L4 部門與組織樹
    # ==========================================
    else:
        st.markdown("#### ➕ 新增擴編組織部門 (支持 L1～L4 階層動態擴充)")
        st.caption("當未來公司擴編、成立新廠區或新部門時，在此直接輸入部門代碼與名稱即可動態建立，完全不需修改程式碼。")

        # 顯示現有部門清單供檢視
        try:
            with engine.connect() as conn:
                df_depts = pd.read_sql("SELECT dept_code as 部門代碼, dept_name as 部門名稱, parent_dept as 上級部門, level_tier as 組織層級 FROM sys_departments", conn)
                st.dataframe(df_depts, use_container_width=True)
        except Exception:
            pass

        st.markdown("---")
        with st.form("add_dept_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_code = st.text_input("部門代碼 (例如: ESG, RD_CENTER)", placeholder="請輸入英文代碼")
                new_name = st.text_input("部門正式名稱 (例如: ESG 永續發展室)", placeholder="請輸入部門名稱")
            with col2:
                parent_opt = st.selectbox("上級所屬部門", ["總公司", "管理部 (Management Dept)", "工程與設計管理中心", "生產製造與倉庫管理"])
                tier_opt = st.selectbox("組織層級 (Tier)", ["L1 (最高決策/一級部門)", "L2 (營運/二級部門)", "L3 (課級/三級部門)", "L4 (組級/四級部門)"])

            submitted_new = st.form_submit_button("🚀 確認新增擴編部門", type="primary", use_container_width=True)

            if submitted_new:
                if new_code and new_name:
                    try:
                        tier_code = tier_opt.split(" ")[0]
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO sys_departments (dept_code, dept_name, parent_dept, level_tier, updated_at)
                                VALUES (:code, :name, :parent, :tier, CURRENT_TIMESTAMP)
                                ON CONFLICT (dept_code) DO UPDATE 
                                SET dept_name = :name, parent_dept = :parent, level_tier = :tier, updated_at = CURRENT_TIMESTAMP
                            """), {
                                "code": new_code.upper().strip(),
                                "name": new_name.strip(),
                                "parent": parent_opt,
                                "tier": tier_code
                            })
                        st.success(f"🎉 成功擴編新增部門：[{tier_code}] {new_name}！資料庫已同步更新。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 新增部門失敗: {e}")
                else:
                    st.warning("⚠️ 請完整填寫部門代碼與名稱。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
