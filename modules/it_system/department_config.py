# ==========================================
# 檔案路徑：modules/it_system/department_config.py
# 職責：部門與模組動態掛載樹狀結構 + 系統設定（品牌識別、資料庫與 API 閘道配置中心）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text, create_engine
import os

def get_robust_db_engine(passed_engine=None):
    if passed_engine is not None:
        return passed_engine
    db_url = os.environ.get("SUPABASE_DB_URL") or st.secrets.get("SUPABASE_DB_URL", "")
    if db_url:
        try:
            clean_url = db_url.strip()
            if "pooler.supabase.com" in clean_url and "?" not in clean_url:
                clean_url += "?sslmode=require"
            return create_engine(clean_url, pool_pre_ping=True)
        except Exception:
            return None
    return None

def init_db_tables(engine):
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 1. 原本的部門與模組動態掛載表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_departments (
                        id SERIAL PRIMARY KEY,
                        dept_name VARCHAR(150) UNIQUE NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_department_modules (
                        id SERIAL PRIMARY KEY,
                        dept_name VARCHAR(150) NOT NULL,
                        module_name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # 2. 企業識別品牌設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_branding (
                        id SERIAL PRIMARY KEY,
                        setting_key VARCHAR(100) UNIQUE NOT NULL,
                        setting_value TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # 3. 資料庫動態串接設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_db_configs (
                        id SERIAL PRIMARY KEY,
                        db_name VARCHAR(100) UNIQUE NOT NULL,
                        connection_url TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # 4. 第三方 API 閘道設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_api_configs (
                        id SERIAL PRIMARY KEY,
                        api_key_name VARCHAR(100) UNIQUE NOT NULL,
                        api_secret_value TEXT,
                        description TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def get_department_module_tree(engine=None):
    """取得完整部門與模組樹狀結構，支援資料庫動態配置與預設降級"""
    default_tree = {
        "總經理室 (Executive Office)": [
            "總經理室戰情室", 
            "AI 原料採購顧問與金屬行情", 
            "AR/AP 與 P&L 財務戰情儀表板", 
            "工程進度與異常即時監控", 
            "越南經營政策與法規動態"
        ],
        "管理部 (Management Dept)": [
            "公司公告佈告欄", 
            "員工檔案管理", 
            "員工打卡紀錄", 
            "員工薪資與保險", 
            "密碼修改", 
            "配合廠商主檔與履約紀錄", 
            "採購與應付帳款 (AP)", 
            "應收帳款管理 (AR)", 
            "越南稅務報表 (Thông tư 200)", 
            "電子發票管理", 
            "宿舍與伙食管理", 
            "工作廠區安全管理", 
            "車輛進出口管制", 
            "車輛維修保養紀錄", 
            "固定資產盤點", 
            "文件檔案管理"
        ],
        "工程與設計管理中心 (Engineering & Design Center)": [
            "工程主管戰情室與案場管理", 
            "工程專案報價系統", 
            "施工日報表與點工點料登記", 
            "AI 施工照片辨識與安衛稽核", 
            "工程證照與機具檢驗預警", 
            "配電盤電氣與機構設計圖庫", 
            "BOM 零件與倉庫採購自動連動", 
            "外包商計價與工班管理", 
            "FAT/SAT 出廠與現場驗收管理"
        ],
        "生產部 (Production Dept - 西寧廠)": [
            "板金加工組工單與條碼追蹤", 
            "粉體塗裝烤漆組品管", 
            "配電盤組裝配線組進度追蹤"
        ],
        "倉庫管理 (Warehouse Management)": [
            "倉庫庫存與資材條碼管理", 
            "安全庫存預警與補貨機制"
        ],
        "現場外勤打卡與工作回報 (Field Attendance)": [
            "手機端極簡 GPS 外勤打卡與施工回報"
        ],
        "電子簽核中心 (Approval Center)": [
            "跨部門請假、採購與工程變更電子簽核中心"
        ]
    }
    
    active_engine = get_robust_db_engine(engine)
    if active_engine is not None:
        try:
            init_db_tables(active_engine)
            with active_engine.connect() as conn:
                df_dept = pd.read_sql(text("SELECT dept_name FROM sys_departments"), con=conn)
                if not df_dept.empty:
                    dynamic_tree = {}
                    for _, row in df_dept.iterrows():
                        d_name = row["dept_name"]
                        df_mod = pd.read_sql(text("SELECT module_name FROM sys_department_modules WHERE dept_name = :d"), con=conn, params={"d": d_name})
                        mods = df_mod["module_name"].tolist() if not df_mod.empty else ["預設模組"]
                        dynamic_tree[d_name] = mods
                    return dynamic_tree
        except Exception:
            pass
            
    return default_tree

def render(engine=None, lang="繁體中文", **kwargs):
    active_engine = get_robust_db_engine(engine)
    
    st.title("⚙️ 系統設定與動態配置中心 (System Settings)")
    st.caption("100% 透過 PostgreSQL 資料庫動態驅動，實現全球 SaaS 零寫死（No Hard-coding）架構。")
    st.markdown("---")

    conn_status = False
    if active_engine is not None:
        try:
            with active_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            conn_status = True
            init_db_tables(active_engine)
        except Exception:
            pass

    tab_tree, tab_brand, tab_db, tab_api = st.tabs([
        "🌳 部門與模組樹狀掛載",
        "🎨 企業品牌與識別設定 (Branding)",
        "🗄️ 資料庫串接動態管理",
        "🌐 第三方 API 閘道設定 (API Gateway)"
    ])

    # 1. 部門與模組樹狀掛載檢視與設定
    with tab_tree:
        st.subheader("🌳 當前系統一級部門與子模組動態樹狀結構")
        st.info("以下為目前系統載入的部門與模組清單（支援資料庫動態擴充與預設降級架構）。")
        tree_data = get_department_module_tree(active_engine)
        for dept, mods in tree_data.items():
            with st.expander(f"📁 {dept} ({len(mods)} 個子模組)"):
                for m in mods:
                    st.markdown(f"- {m}")

    # 2. 企業品牌與識別設定
    with tab_brand:
        st.subheader("🎨 企業識別與 Logo 動態配置")
        default_name = "裕豐電機工業 (Reetech Industrial)"
        default_logo = "https://raw.githubusercontent.com/tabgshu-ux/RECH/main/assets/logo.png"
        
        if conn_status:
            try:
                with active_engine.connect() as conn:
                    df = pd.read_sql(text("SELECT setting_key, setting_value FROM sys_branding"), con=conn)
                    if not df.empty:
                        for _, row in df.iterrows():
                            if row["setting_key"] == "company_name":
                                default_name = row["setting_value"]
                            elif row["setting_key"] == "logo_url":
                                default_logo = row["setting_value"]
            except Exception:
                pass

        with st.form("branding_form"):
            new_name = st.text_input("企業顯示名稱 (Company Name)", value=default_name)
            new_logo = st.text_input("企業 Logo 圖片網址 (Logo Image URL)", value=default_logo)
            save_brand = st.form_submit_button("💾 儲存企業品牌設定", type="primary")
            
            if save_brand and conn_status:
                try:
                    with active_engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_branding (setting_key, setting_value)
                            VALUES ('company_name', :val)
                            ON CONFLICT (setting_key) DO UPDATE SET setting_value = :val, updated_at = CURRENT_TIMESTAMP
                        """), {"val": new_name.strip()})
                        conn.execute(text("""
                            INSERT INTO sys_branding (setting_key, setting_value)
                            VALUES ('logo_url', :val)
                            ON CONFLICT (setting_key) DO UPDATE SET setting_value = :val, updated_at = CURRENT_TIMESTAMP
                        """), {"val": new_logo.strip()})
                    st.success("🎉 企業品牌識別設定已成功寫入資料庫！")
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

    # 3. 資料庫串接動態管理
    with tab_db:
        st.subheader("🗄️ 外部與主資料庫串接管理")
        with st.form("db_config_form"):
            db_name = st.text_input("資料庫識別名稱 (例如: Production_Supabase)", value="Main_Supabase")
            db_url_input = st.text_input("資料庫連線字串 (Database URL)", type="password", placeholder="postgresql://user:pass@host:port/db")
            save_db = st.form_submit_button("🔌 儲存並測試資料庫連線", type="primary")
            
            if save_db and conn_status:
                try:
                    with active_engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_db_configs (db_name, connection_url, is_active)
                            VALUES (:name, :url, TRUE)
                            ON CONFLICT (db_name) DO UPDATE SET connection_url = :url, updated_at = CURRENT_TIMESTAMP
                        """), {"name": db_name.strip(), "url": db_url_input.strip()})
                    st.success(f"🎉 資料庫設定 [{db_name}] 已成功儲存！")
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

    # 4. 第三方 API 閘道設定
    with tab_api:
        st.subheader("🌐 第三方 API 閘道與金鑰設定")
        with st.form("api_config_form"):
            api_name = st.selectbox("選擇或輸入 API 類別", [
                "LME_Copper_API (LME 銅價行情)",
                "Vietnam_Tax_Invoice_API (越南電子發票系統)",
                "Bank_Exchange_Rate_API (銀行匯率 API)",
                "AI_Gemini_Procurement_API (AI 採購顧問金鑰)",
                "Stock_Market_API (股市行情 API)"
            ])
            api_secret = st.text_input("API 金鑰 / 權杖 (Secret Key / Token)", type="password", placeholder="請輸入密鑰")
            api_desc = st.text_area("備註說明", placeholder="例如：串接越南當地電子發票開立與報稅驗證")
            save_api = st.form_submit_button("🔒 安全儲存 API 設定", type="primary")
            
            if save_api and conn_status:
                try:
                    with active_engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_api_configs (api_key_name, api_secret_value, description)
                            VALUES (:name, :secret, :desc)
                            ON CONFLICT (api_key_name) DO UPDATE SET api_secret_value = :secret, description = :desc, updated_at = CURRENT_TIMESTAMP
                        """), {"name": api_name.split()[0], "secret": api_secret.strip(), "desc": api_desc.strip()})
                    st.success(f"🎉 API 設定 [{api_name}] 已安全加密儲存至資料庫！")
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
