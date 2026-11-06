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
    st.title("⚙️ 部門與模組動態掛載中心")
    st.write("在此管理系統的一級部門與子模組掛載。")
