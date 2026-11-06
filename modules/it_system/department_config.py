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
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_api_configs (
                        id SERIAL PRIMARY KEY,
                        config_key VARCHAR(100) UNIQUE NOT NULL,
                        config_value TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # 建立企業動態設定表 (Metadata-driven branding)
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_branding (
                        id SERIAL PRIMARY KEY,
                        setting_key VARCHAR(100) UNIQUE NOT NULL,
                        setting_value TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

def get_company_branding(engine=None):
    """從資料庫動態讀取公司名稱與 Logo 設定，實現零寫死 (No Hard-coding)"""
    default_branding = {
        "company_name": "裕豐電機工業 (Reetech Industrial)",
        "logo_url": "https://raw.githubusercontent.com/tabgshu-ux/RECH/main/assets/logo.png"
    }
    active_engine = get_robust_db_engine(engine)
    if active_engine is not None:
        try:
            init_db_tables(active_engine)
            with active_engine.connect() as conn:
                df = pd.read_sql(text("SELECT setting_key, setting_value FROM sys_branding"), con=conn)
                if not df.empty:
                    for _, row in df.iterrows():
                        if row["setting_key"] in default_branding:
                            default_branding[row["setting_key"]] = row["setting_value"]
        except Exception:
            pass
    return default_branding

def render(engine=None, lang="繁體中文", **kwargs):
    active_engine = get_robust_db_engine(engine)
    
    st.title("⚙️ 系統設定、資料庫與動態網頁配置中心")
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

    tab_brand, tab_dept, tab_api = st.tabs([
        "🎨 企業識別與品牌設定 (Branding)",
        "🏢 企業部門與模組動態掛載",
        "🌐 第三方 API 閘道設定"
    ])

    with tab_brand:
        st.subheader("🎨 企業品牌與 Logo 動態配置")
        st.info("在此設定的企業名稱與 Logo 將直接儲存於資料庫，全系統自動即時渲染，完全不需修改程式碼。")
        
        current_branding = get_company_branding(active_engine)
        
        with st.form("branding_config_form"):
            new_comp_name = st.text_input("企業顯示名稱 (Company Name)", value=current_branding["company_name"])
            new_logo_url = st.text_input("企業 Logo 圖片網址 (Logo Image URL)", value=current_branding["logo_url"])
            
            save_brand = st.form_submit_button("💾 儲存企業品牌設定至資料庫", type="primary")
            if save_brand and conn_status:
                try:
                    with active_engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_branding (setting_key, setting_value)
                            VALUES ('company_name', :val)
                            ON CONFLICT (setting_key) DO UPDATE SET setting_value = :val, updated_at = CURRENT_TIMESTAMP
                        """), {"val": new_comp_name.strip()})
                        
                        conn.execute(text("""
                            INSERT INTO sys_branding (setting_key, setting_value)
                            VALUES ('logo_url', :val)
                            ON CONFLICT (setting_key) DO UPDATE SET setting_value = :val, updated_at = CURRENT_TIMESTAMP
                        """), {"val": new_logo_url.strip()})
                    st.success("🎉 企業識別設定已成功寫入資料庫！")
                    st.rerun()
                except Exception as e:
                    st.error(f"儲存失敗: {e}")

        st.markdown("---")
        st.markdown("#### 👁️ 當前 Logo 與名稱預覽：")
        cols = st.columns([1, 4])
        with cols[0]:
            try:
                st.image(current_branding["logo_url"], width=80)
            except Exception:
                st.warning("Logo 載入失敗")
        with cols[1]:
            st.markdown(f"### {current_branding['company_name']}")

    with tab_dept:
        st.subheader("🏢 資料庫部門與模組動態管理")
        tree = get_department_module_tree(active_engine)
        for d_name, mods in tree.items():
            with st.expander(f"📁 {d_name} (包含 {len(mods)} 項模組)"):
                for m in mods:
                    st.markdown(f"• {m}")

    with tab_api:
        st.subheader("🌐 第三方 API 閘道設定")
        st.info("管理系統對接外部 API 的密鑰與端點。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
