# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：1~4 級動態部門樹狀掛載、修正中文代碼衝突導致覆蓋的重大 Bug、自動 Seed 防護
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
    """初始化系統設定資料表與預設根目錄部門"""
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

                # 自動植入預設核心大部門（若表格為空）
                res = conn.execute(text("SELECT COUNT(*) FROM sys_departments")).scalar()
                if res == 0:
                    default_depts = [
                        ("gm", None, "L1", "總經理室", "Văn phòng Tổng Giám đốc"),
                        ("mgmt", None, "L1", "管理部", "Bộ phận Quản lý"),
                        ("eng", None, "L1", "工程部", "Bộ phận Công trình"),
                        ("prod", None, "L1", "生產部", "Bộ phận Sản xuất"),
                        ("wh", None, "L1", "倉庫管理", "Quản lý kho"),
                        ("approval", None, "L1", "簽核中心", "Trung tâm phê duyệt")
                    ]
                    for code, parent, lvl, zh, vi in default_depts:
                        conn.execute(text("""
                            INSERT INTO sys_departments (dept_code, parent_code, level_depth, dept_name_zh, dept_name_vi, is_active)
                            VALUES (:code, :parent, :lvl, :zh, :vi, TRUE)
                            ON CONFLICT (dept_code) DO NOTHING;
                        """), {"code": code, "parent": parent, "lvl": lvl, "zh": zh, "vi": vi})

                    default_mods = [
                        ("mgmt", "管理部主管綜合戰情儀表板"),
                        ("mgmt", "人事行政課 — 員工檔案、考勤與薪資管理"),
                        ("gm", "總經理室戰情室"),
                        ("eng", "工程主管戰情室與案場管理")
                    ]
                    for d_code, m_name in default_mods:
                        conn.execute(text("""
                            INSERT INTO sys_department_modules (dept_code, module_name)
                            VALUES (:d_code, :m_name)
                            ON CONFLICT DO NOTHING;
                        """), {"d_code": d_code, "m_name": m_name})
        except Exception:
            pass

def get_department_module_tree(engine=None):
    active_engine = get_robust_db_engine(engine)
    dynamic_tree = {}
    
    if active_engine is not None:
        try:
            reset_and_init_db_tables(active_engine)
            with active_engine.connect() as conn:
                df_dept = pd.read_sql(text("SELECT dept_code, dept_name_zh, level_depth FROM sys_departments WHERE is_active = TRUE"), con=conn)
                if not df_dept.empty:
                    for _, row in df_dept.iterrows():
                        d_code = row["dept_code"]
                        d_name = row["dept_name_zh"]
                        d_level = row["level_depth"]
                        df_mod = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :d"), con=conn, params={"d": d_code})
                        mods = df_mod["module_name"].tolist() if not df_mod.empty else ["尚未掛載模組"]
                        dynamic_tree[f"[{d_level}] {d_name} ({d_code})"] = mods
                    return dynamic_tree
        except Exception:
            pass
            
    return {
        "[L1] 管理部 (mgmt)": ["管理部主管綜合戰情儀表板"]
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
    st.info("在此動態維護公司組織架構，系統已全面修復中文代碼衝突，可順利建立多個獨立部門與二級課室。")

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
        "🌳 現有部門與模組樹狀檢視", 
        "➕ 新增 1~4 級部門與模組掛載", 
        "📋 現有部門清單與模組調整/裁撤"
    ])

    with tab_tree:
        st.markdown("##### 🌳 當前系統一級/二級部門與掛載子模組動態樹狀結構")
        tree_data = get_department_module_tree(active_engine)
        if not tree_data:
            st.info("目前尚無任何部門資料。")
        else:
            for dept, mods in tree_data.items():
                with st.expander(f"📁 {dept} ({len(mods)} 個掛載模組)"):
                    for m in mods:
                        st.markdown(f"- {m}")

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
                "財務會計課 — 電子發票管理與歸檔": "對接越南電子發票系統進行開立、查驗與 XML 歸檔",
                "總務後勤 — 幹部宿舍與伙食管理": "管理幹部宿舍分配、水電費與員工伙食採購",
                "總務後勤 — 廠區車輛與門禁管理": "記錄廠區貨車、小客車進出門禁與磅秤紀錄",
                "總務後勤 — 車輛維修與固定資產盤點": "管理公務車維修保養及廠內生財器具盤點"
            },
            "✍️ 跨部門電子簽核中心 (Approval Center)": {
                "跨部門電子簽核中心主控台": "統一管理全公司請假、採購、工程變更與財務撥款的電子簽核流程",
                "待簽核單據彙整與主管簽核": "提供各級主管快速進行審核、退回或批示的互動介面"
            },
            "📊 總經理室與戰情決策": {
                "總經理室戰情室": "彙整全廠營運績效、KPI 達成率與重大異常警示",
                "AI 原料採購顧問與金屬行情": "即時分析 LME 銅價與原物料走勢提供採購建議",
                "AR/AP 與 P&L 財務戰情儀表板": "掌握應收應付帳款與損益狀況",
                "工程進度與異常即時監控": "全盤掌握各地工程案場進度與工安異常",
                "越南經營政策與法規動態": "追蹤越南當地最新稅務、勞動法規與政策異動"
            },
            "🛠️ 工程與現場作業管理": {
                "工程主管戰情室與案場管理": "統籌各案場施工能量、進度回報與工班調度",
                "工程專案報價系統": "針對高低壓配電盤及 MEP 工程進行快速報價試算",
                "現場外勤打卡與作業登記": "提供越籍與台幹手機端 GPS 打卡及現場回報",
                "施工日報表與點工點料登記": "每日記錄施工現場點工數與耗用材料",
                "AI 施工照片辨識與安衛稽核": "透過 AI 自動辨識施工照片並進行安衛合規檢查",
                "工程證照與機具檢驗預警": "自動發出證照到期與吊車/電氣機具檢驗警報",
                "配電盤電氣與機構設計圖庫": "集中管理配電盤電路圖、CAD 與機構設計圖檔",
                "BOM 零件與倉庫採購自動連動": "自動將工程設計 BOM 拆解並連動倉庫採購",
                "外包商計價與工班管理": "管理外部施工工班計價、出工數與工程款撥付",
                "FAT/SAT 出廠與現場驗收管理": "記錄出廠測試 (FAT) 及現場驗收 (SAT) 簽核"
            },
            "🏭 生產製造與倉儲管理": {
                "倉庫庫存與資材條碼管理": "管理倉庫進出貨、庫存水位與條碼掃描作業",
                "板金加工組工單與條碼追蹤": "追蹤西寧廠板金裁切、折彎與沖孔工單進度",
                "粉體塗裝烤漆組品管": "記錄烤漆膜厚、色差與靜電粉體塗裝品管數據",
                "配電盤組裝配線組進度追蹤": "監控配電盤銅排加工、配線與組裝進度",
                "工作廠區安全管理": "管理廠區安全規範、消防設施與安衛巡檢"
            }
        }

        with st.form("add_department_hierarchy_form"):
            parent_dept = st.selectbox(
                "上層所屬部門 (Parent Department)", 
                [
                    "無 (根目錄 / 一級大部門)", 
                    "總經理室 (Executive Office)", 
                    "管理部 (Management Dept)", 
                    "工程部 (Engineering Dept)", 
                    "生產部 (Production Dept)", 
                    "倉庫管理 (Warehouse)", 
                    "簽核中心 (Approval Center)"
                ]
            )
            
            level_choice = st.selectbox(
                "部門層級 (Hierarchy Level)", 
                [
                    "L1 - 大部門 / 事業處 (例如: 管理部、工程部、生產部)",
                    "L2 - 二級部門 / 課室 (例如: 人事行政課、總務採購課、財務會計課)",
                    "L3 - 三級組別 / 專案小組 (例如: 員工合約組、配電盤配線組)",
                    "L4 - 四級現場作業站 / 點工班 (例如: 西寧廠 A 區焊工班、外勤安裝班)"
                ]
            )
            
            name_zh = st.text_input("部門繁體中文名稱 *", placeholder="例如: 管理部, 人事行政課, 簽核中心")
            name_vi = st.text_input("部門越文名稱 (Tiếng Việt)", placeholder="Ví dụ: Bộ phận Quản lý")
            
            st.markdown("---")
            st.markdown("#### 🧩 勾選並掛載此部門可操作的業務模組（附帶詳細功用說明）：")

            selected_department_modules = []
            for cat_name, mod_dict in ALL_AVAILABLE_MODULES.items():
                with st.expander(f"{cat_name} （包含 {len(mod_dict)} 項功能）", expanded=False):
                    for mod_name, mod_desc in mod_dict.items():
                        label_text = f"**{mod_name}** — 📝 *{mod_desc}*"
                        if st.checkbox(label_text, key=f"chk_dept_mod_{mod_name}"):
                            selected_department_modules.append(mod_name)

            st.markdown("---")
            submitted = st.form_submit_button("💾 儲存部門設定並掛載模組", type="primary", use_container_width=True)
            
            if submitted:
                if not name_zh:
                    st.error("⚠️ 請至少填寫部門繁體中文名稱！")
                else:
                    # 🌟 關鍵修復：改用時間戳記生成絕對唯一的 dept_code，絕不發生中文名稱碰撞覆蓋
                    unique_code = f"dept_{int(time.time()*1000)}"
                    
                    if conn_status:
                        try:
                            with active_engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO sys_departments (dept_code, parent_code, level_depth, dept_name_zh, dept_name_vi, is_active)
                                    VALUES (:code, :parent, :lvl, :zh, :vi, TRUE)
                                """), {
                                    "code": unique_code,
                                    "parent": parent_dept.split()[0],
                                    "lvl": level_choice.split()[0],
                                    "zh": name_zh.strip(),
                                    "vi": name_vi.strip()
                                })
                                
                                for m_name in selected_department_modules:
                                    conn.execute(text("""
                                        INSERT INTO sys_department_modules (dept_code, module_name)
                                        VALUES (:code, :m_name)
                                    """), {"code": unique_code, "m_name": m_name})

                            st.success(f"🎉 成功新增部門 [{name_zh}]（代碼: {unique_code}）並掛載了 {len(selected_department_modules)} 個模組！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 寫入資料庫失敗: {e}")
                    else:
                        st.success(f"🎉 成功新增部門 [{name_zh}]（模擬模式）！")

    with tab_manage:
        st.markdown("##### 📋 現有部門清單與模組即時調整 / 移除管理")
        st.caption("您可以隨時選取某個部門來**增減掛載的模組**，或直接將該部門安全停用。")

        if conn_status:
            try:
                df_existing = pd.read_sql("SELECT dept_code, dept_name_zh, dept_name_vi FROM sys_departments WHERE is_active = TRUE", con=active_engine)
                if not df_existing.empty:
                    dept_options = {row["dept_name_zh"]: row["dept_code"] for _, row in df_existing.iterrows()}
                    selected_target_dept_name = st.selectbox("🎯 選擇要調整模組或管理的部門", list(dept_options.keys()))
                    target_code = dept_options[selected_target_dept_name]

                    df_current_mods = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_code = :code"), con=active_engine, params={"code": target_code})
                    current_assigned = df_current_mods["module_name"].tolist() if not df_current_mods.empty else []

                    st.markdown(f"**當前部門 [{selected_target_dept_name}] 已掛載的模組數：** {len(current_assigned)} 個")
                    
                    if current_assigned:
                        st.markdown("###### 🗑️ 勾選並移除不需要的模組：")
                        mods_to_remove = []
                        for cm in current_assigned:
                            if st.checkbox(f"移除模組: {cm}", key=f"remove_mod_{target_code}_{cm}*"):
                                mods_to_remove.append(cm)

                        if st.button("🗑️ 確認從此部門移除勾選的模組", type="secondary"):
                            if mods_to_remove:
                                with active_engine.begin() as conn:
                                    for rm in mods_to_remove:
                                        conn.execute(text("DELETE FROM sys_department_modules WHERE dept_code = :code AND module_name = :rm"), {"code": target_code, "rm": rm})
                                st.success(f"🎉 已成功移除 {len(mods_to_remove)} 個模組！")
                                st.rerun()
                            else:
                                st.warning("⚠️ 請先勾選要移除的模組。")
                    else:
                        st.info("此部門目前尚無掛載任何模組。")

                    st.markdown("---")
                    if st.button(f"🗑️ 執行部門 [{selected_target_dept_name}] 永久裁撤/停用", type="primary"):
                        with active_engine.begin() as conn:
                            conn.execute(text("UPDATE sys_departments SET is_active = FALSE WHERE dept_code = :code"), {"code": target_code})
                        st.warning(f"⚠️ 部門 [{selected_target_dept_name}] 已成功停用與歸檔！")
                        st.rerun()
                else:
                    st.info("目前尚無建立任何部門。")
            except Exception as e:
                st.error(f"讀取部門資料失敗: {e}")
        else:
            st.info("資料庫未連線。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
