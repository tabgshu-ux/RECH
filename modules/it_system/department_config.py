# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：1~4 級動態組織配置中心（支援完全動態父層選取、L1~L4 彈性升降級與模組自由掛載）
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

                # 若表格為空，初始化預設 L1 根目錄
                res = conn.execute(text("SELECT COUNT(*) FROM sys_departments")).scalar()
                if res == 0:
                    default_depts = [
                        ("gm", "None", "L1", "總經理室", "Văn phòng Tổng Giám đốc"),
                        ("mgmt", "None", "L1", "管理部", "Bộ phận Quản lý"),
                        ("eng", "None", "L1", "工程部", "Bộ phận Công trình"),
                        ("prod", "None", "L1", "生產部", "Bộ phận Sản xuất")
                    ]
                    for code, parent, lvl, zh, vi in default_depts:
                        conn.execute(text("""
                            INSERT INTO sys_departments (dept_code, parent_code, level_depth, dept_name_zh, dept_name_vi, is_active)
                            VALUES (:code, :parent, :lvl, :zh, :vi, TRUE)
                            ON CONFLICT (dept_code) DO NOTHING;
                        """), {"code": code, "parent": parent, "lvl": lvl, "zh": zh, "vi": vi})
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
    st.info("在此動態維護公司組織架構。支援任意部門升降級，上層父部門完全由現有組織動態選取，並自由掛載業務模組。")

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

    tab_tree, tab_add, tab_manage = st.tabs([
        "🌳 現有組織樹狀檢視", 
        "➕ 新增 L1~L4 部門與模組掛載", 
        "📋 現有部門清單與模組調整"
    ])

    # 取得現有部門清單供動態選取父層
    existing_depts_list = [("無 (獨立 L1 頂級部門)", "None")]
    if conn_status:
        try:
            df_all = pd.read_sql("SELECT dept_code, dept_name_zh, level_depth FROM sys_departments WHERE is_active = TRUE", con=active_engine)
            if not df_all.empty:
                for _, r in df_all.iterrows():
                    existing_depts_list.append((f"[{r['level_depth']}] {r['dept_name_zh']}", r['dept_code']))
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
                    # 呈現 L1 及其下屬 L2/L3/L4
                    l1_rows = df_tree[df_tree["level_depth"] == "L1"]
                    for _, l1 in l1_rows.iterrows():
                        l1_mods = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :c"), con=active_engine, params={"c": l1['dept_code']})["module_name"].tolist()
                        with st.expander(f"📂 [L1] {l1['dept_name_zh']} ({len(l1_mods)} 個掛載模組)"):
                            for m in l1_mods:
                                st.markdown(f"  - 📌 {m}")
                            
                            # 尋找下屬子部門
                            sub_rows = df_tree[df_tree["parent_code"] == l1['dept_code']]
                            for _, sub in sub_rows.iterrows():
                                sub_mods = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :c"), con=active_engine, params={"c": sub['dept_code']})["module_name"].tolist()
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;└ 📁 **[{sub['level_depth']}] {sub['dept_name_zh']}** ({len(sub_mods)} 個掛載模組)")
                                for sm in sub_mods:
                                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- 📌 {sm}")
            except Exception as e:
                st.warning(f"載入樹狀結構提示: {e}")

    with tab_add:
        ALL_AVAILABLE_MODULES = {
            "👔 管理部與二級課室 (Management & Sub-depts)": {
                "管理部主管綜合戰情儀表板": "統合請假早退人員名單、當月採購金額花費與車輛維修保養費用統合資料",
                "公司公告佈告欄": "發布公司政策、放假通知與重要公告",
                "人事行政課 — 員工檔案與履約管理": "維護員工個人履歷、護照、工作證與合約資料",
                "人事行政課 — 考勤與打卡紀錄": "統計廠內與外勤員工出勤時數及請假紀錄",
                "人事行政課 — 薪資計算與 BHXH 保險": "計算越籍員工薪資、加班費與社會保險扣除",
                "總務採購課 — 配合廠商主檔與履約紀錄": "管理供應商、外包商信用評等與合約檔案",
                "總務採購課 — 採購單與應付帳款 (AP)": "處理請購、採購發包與供應商應付帳款立帳",
                "財務會計課 — 應收帳款管理 (AR)": "追蹤客戶專案工程款請款進度與收款紀錄",
                "財務會計課 — 越南稅務標準財報 (Thông tư 200)": "自動生成符合越南會計標準 Thông tư 200 的法定報表",
                "總務後勤 — 幹部宿舍與伙食管理": "管理幹部宿舍分配、水電費與員工伙食採購",
                "總務後勤 — 車輛維修與固定資產盤點": "管理公務車維修保養及廠內生財器具盤點"
            },
            "✍️ 跨部門電子簽核中心": {
                "跨部門電子簽核中心主控台": "統一管理全公司請假、採購、工程變更與財務撥款的電子簽核流程",
                "待簽核單據彙整與主管簽核": "提供各級主管快速進行審核、退回或批示的互動介面"
            },
            "📊 總經理室與戰情決策": {
                "總經理室戰情室": "彙整全廠營運績效、KPI 達成率與重大異常警示",
                "AI 原料採購顧問與金屬行情": "即時分析 LME 銅價與原物料走勢提供採購建議",
                "工程進度與異常即時監控": "全盤掌握各地工程案場進度與工安異常"
            },
            "🛠️ 工程與現場作業管理": {
                "工程主管戰情室與案場管理": "統籌各案場施工能量、進度回報與工班調度",
                "工程專案報價系統": "針對高低壓配電盤及 MEP 工程進行快速報價試算",
                "施工日報表與點工點料登記": "每日記錄施工現場點工數與耗用材料",
                "配電盤電氣與機構設計圖庫": "集中管理配電盤電路圖、CAD 與機構設計圖檔"
            },
            "🏭 生產製造與倉儲管理": {
                "倉庫庫存與資材條碼管理": "管理倉庫進出貨、庫存水位與條碼掃描作業",
                "配電盤組裝配線組進度追蹤": "監控配電盤銅排加工、配線與組裝進度"
            }
        }

        with st.form("add_dynamic_dept_form"):
            parent_selection = st.selectbox(
                "上層所屬部門 (Parent Department) —— 選擇歸屬上級", 
                options=[item[0] for item in existing_depts_list]
            )
            # 對應取得父層代碼
            parent_code = next(item[1] for item in existing_depts_list if item[0] == parent_selection)
            
            level_choice = st.selectbox(
                "組織層級 (Hierarchy Level)", 
                [
                    "L1 - 頂級大部門 / 事業處",
                    "L2 - 二級部門 / 課室",
                    "L3 - 三級組別 / 專案小組",
                    "L4 - 四級現場作業站 / 點工班"
                ]
            )
            
            name_zh = st.text_input("部門繁體中文名稱 *", placeholder="例如: 人事行政課, 設計課, 焊工班")
            name_vi = st.text_input("部門越文名稱 (Tiếng Việt)", placeholder="Ví dụ: Phòng Nhân sự")
            
            st.markdown("---")
            st.markdown("#### 🧩 勾選並掛載此部門可操作的業務模組：")

            selected_department_modules = []
            for cat_name, mod_dict in ALL_AVAILABLE_MODULES.items():
                with st.expander(f"{cat_name} （包含 {len(mod_dict)} 項功能）", expanded=False):
                    for mod_name, mod_desc in mod_dict.items():
                        if st.checkbox(f"**{mod_name}** — 📝 *{mod_desc}*", key=f"chk_m_{mod_name}"):
                            selected_department_modules.append(mod_name)

            submitted = st.form_submit_button("💾 儲存組織設定並掛載模組", type="primary", use_container_width=True)
            
            if submitted:
                if not name_zh:
                    st.error("⚠️ 請至少填寫部門繁體中文名稱！")
                else:
                    unique_code = f"dept_{int(time.time()*1000)}"
                    lvl_val = level_choice.split()[0] # 取得 L1, L2, L3 或 L4
                    
                    if conn_status:
                        try:
                            with active_engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO sys_departments (dept_code, parent_code, level_depth, dept_name_zh, dept_name_vi, is_active)
                                    VALUES (:code, :parent, :lvl, :zh, :vi, TRUE)
                                """), {
                                    "code": unique_code,
                                    "parent": parent_code if parent_code != "None" else None,
                                    "lvl": lvl_val,
                                    "zh": name_zh.strip(),
                                    "vi": name_vi.strip()
                                })
                                
                                for m_name in selected_department_modules:
                                    conn.execute(text("""
                                        INSERT INTO sys_department_modules (dept_code, module_name)
                                        VALUES (:code, :m_name)
                                    """), {"code": unique_code, "m_name": m_name})

                            st.success(f"🎉 成功新增 [{lvl_val}] 部門 [{name_zh}] 並掛載了 {len(selected_department_modules)} 個模組！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 寫入資料庫失敗: {e}")
                    else:
                        st.success(f"🎉 成功新增 [{lvl_val}] 部門 [{name_zh}]（模擬模式）！")

    with tab_manage:
        st.markdown("##### 📋 現有部門清單與模組即時調整")
        if conn_status:
            try:
                df_existing = pd.read_sql("SELECT dept_code, dept_name_zh, level_depth FROM sys_departments WHERE is_active = TRUE", con=active_engine)
                if not df_existing.empty:
                    dept_options = {f"[{row['level_depth']}] {row['dept_name_zh']}": row["dept_code"] for _, row in df_existing.iterrows()}
                    selected_target = st.selectbox("🎯 選擇要調整的部門", list(dept_options.keys()))
                    target_code = dept_options[selected_target]

                    df_current_mods = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :code"), con=active_engine, params={"code": target_code})
                    current_assigned = df_current_mods["module_name"].tolist() if not df_current_mods.empty else []

                    st.markdown(f"**當前已掛載模組數：** {len(current_assigned)} 個")
                    if current_assigned:
                        mods_to_remove = []
                        for cm in current_assigned:
                            if st.checkbox(f"移除模組: {cm}", key=f"rm_{target_code}_{cm}"):
                                mods_to_remove.append(cm)

                        if st.button("🗑️ 確認移除勾選模組", type="secondary"):
                            if mods_to_remove:
                                with active_engine.begin() as conn:
                                    for rm in mods_to_remove:
                                        conn.execute(text("DELETE FROM sys_department_modules WHERE dept_code = :code AND module_name = :rm"), {"code": target_code, "rm": rm})
                                st.success("🎉 模組移除成功！")
                                st.rerun()
                    
                    st.markdown("---")
                    if st.button("🗑️ 永久裁撤/停用此部門", type="primary"):
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
