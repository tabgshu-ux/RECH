# ==========================================
# 檔案路徑：modules/it_system/branding_config.py
# 職責：企業識別與品牌 Logo 動態配置（支援資料表自動建立、實體圖檔儲存與即時刷新）
# ==========================================

import streamlit as st
import os
from sqlalchemy import text

def init_tenant_settings_table(engine):
    """自動初始化 tenant_settings 資料表，防止資料庫寫入失敗"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS tenant_settings (
                        tenant_id VARCHAR(50) PRIMARY KEY,
                        company_name VARCHAR(255),
                        company_subtitle VARCHAR(255),
                        logo_url VARCHAR(255),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"⚠️ 初始化品牌設定資料表發生異常: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🎨 企業品牌與識別設定 (Tenant Branding & Logo Management)")
    st.caption("多租戶白標設定：在此變更公司名稱、副標題與上傳企業專屬 Logo，系統將自動套用至全站側邊欄。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎 (`engine`)，目前為離線展示模式。")
        return

    # 確保資料表存在
    init_tenant_settings_table(engine)

    current_tenant_id = st.session_state.get("tenant_id", "REETECH_VN")

    # 讀取現有品牌設定
    current_name = "裕豐電機工業有限公司"
    current_sub = "CÔNG TY TNHH CN DỮ PHONG"
    current_logo = ""

    try:
        with engine.connect() as conn:
            res = conn.execute(
                text("SELECT company_name, company_subtitle, logo_url FROM tenant_settings WHERE tenant_id = :tid"),
                {"tid": current_tenant_id}
            ).fetchone()
            if res:
                current_name = res[0] or current_name
                current_sub = res[1] or current_sub
                current_logo = res[2] or ""
    except Exception:
        current_name = st.session_state.get("tenant_company_name", "裕豐電機工業有限公司")
        current_sub = st.session_state.get("tenant_company_sub", "CÔNG TY TNHH CN DỮ PHONG")

    with st.form("branding_form"):
        new_company_name = st.text_input("企業正式名稱 (Company Name)", value=current_name)
        new_company_sub = st.text_input("企業副標題 / 越文名稱 (Subtitle / Local Name)", value=current_sub)
        
        # 顯示目前已上傳的 Logo 狀態
        if current_logo:
            st.text(sprintf := f"📁 當前 Logo 儲存路徑: {current_logo}")
            
        uploaded_logo = st.file_uploader("上傳企業 Logo 圖片 (建議尺寸 200x60px, PNG/JPG)", type=["png", "jpg", "jpeg"])
        
        submitted_brand = st.form_submit_button("💾 儲存並即時更新企業識別 (Save Branding)", type="primary", use_container_width=True)
        
        if submitted_brand:
            logo_path = current_logo
            
            # 修正：確實將上傳的圖片檔案寫入實體資料夾中
            if uploaded_logo is not None:
                try:
                    os.makedirs("assets", exist_ok=True)
                    logo_path = f"assets/{current_tenant_id}_{uploaded_logo.name}"
                    with open(logo_path, "wb") as f:
                        f.write(uploaded_logo.getbuffer())
                except Exception as file_err:
                    st.warning(f"⚠️ 圖檔儲存至伺服器失敗: {file_err}")

            try:
                with engine.begin() as conn:
                    upsert_sql = text("""
                        INSERT INTO tenant_settings (tenant_id, company_name, company_subtitle, logo_url, updated_at)
                        VALUES (:tid, :cname, :csub, :lurl, CURRENT_TIMESTAMP)
                        ON CONFLICT (tenant_id) 
                        DO UPDATE SET company_name = :cname, company_subtitle = :csub, logo_url = :lurl, updated_at = CURRENT_TIMESTAMP
                    """)
                    conn.execute(upsert_sql, {
                        "tid": current_tenant_id,
                        "cname": new_company_name,
                        "csub": new_company_sub,
                        "lurl": logo_path
                    })
                
                # 同步更新 session_state
                st.session_state.tenant_company_name = new_company_name
                st.session_state.tenant_company_sub = new_company_sub
                st.session_state.tenant_logo_url = logo_path
                
                st.success("🎉 企業品牌識別已成功寫入資料庫！側邊欄與標題已同步更新。")
                st.rerun()
            except Exception as db_err:
                st.error(f"❌ 資料庫儲存失敗: {db_err}")
