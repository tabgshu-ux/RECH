# ==========================================
# 檔案路徑：modules/it_system/branding_config.py
# 職責：企業識別與品牌 Logo 動態配置（支援手動預設設定與 AD 群組自動對應連結）
# ==========================================

import streamlit as st
import os
from sqlalchemy import text

def init_tenant_settings_table(engine):
    """自動初始化 tenant_settings 與 ad_group_branding_mapping 資料表，確保資料庫寫入萬無一失"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 1. 預設租戶設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS tenant_settings (
                        tenant_id VARCHAR(50) PRIMARY KEY,
                        company_name VARCHAR(255),
                        company_subtitle VARCHAR(255),
                        logo_url VARCHAR(255),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # 2. AD 群組對應品牌設定表（支援 Active Directory 群組名稱聯動）
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ad_group_branding_mapping (
                        id SERIAL PRIMARY KEY,
                        ad_group_name VARCHAR(255) UNIQUE NOT NULL,
                        mapped_company_name VARCHAR(255),
                        mapped_subtitle VARCHAR(255),
                        mapped_logo_url VARCHAR(255),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"⚠️ 初始化品牌設定與 AD 對應資料表發生異常: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🎨 企業品牌與識別設定 (Tenant Branding & AD Group Mapping)")
    st.caption("多租戶白標設定：在此變更預設公司名稱、副標題與上傳企業專屬 Logo，亦可設定 Active Directory (AD) 群組名稱對應連結，根據使用者所屬 AD 自動切換對應識別。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎 (`engine`)，目前為離線展示模式。")
        return

    # 確保資料表存在
    init_tenant_settings_table(engine)
    current_tenant_id = st.session_state.get("tenant_id", "REETECH_VN")

    # 建立分頁：分流「手動預設設定」與「AD 群組名稱連結設定」
    tab_manual, tab_ad_mapping = st.tabs(["🏢 手動企業識別設定 (Default Branding)", "🔗 AD 群組連結對應設定 (AD Group Mapping)"])

    # ==========================================
    # 分頁一：手動企業識別設定（您原本的完整邏輯）
    # ==========================================
    with tab_manual:
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
            current_logo = st.session_state.get("tenant_logo_url", "")

        with st.form("branding_form"):
            new_company_name = st.text_input("企業正式名稱 (Company Name)", value=current_name)
            new_company_sub = st.text_input("企業副標題 / 越文名稱 (Subtitle / Local Name)", value=current_sub)
            
            if current_logo:
                st.caption(f"📁 目前生效的 Logo 檔案路徑: `{current_logo}`")
                if os.path.exists(current_logo):
                    st.image(current_logo, width=150)

            uploaded_logo = st.file_uploader("上傳企業 Logo 圖片 (建議尺寸 200x60px, PNG/JPG)", type=["png", "jpg", "jpeg"])
            
            submitted_brand = st.form_submit_button("💾 儲存並即時更新企業識別 (Save Branding)", type="primary", use_container_width=True)
            
            if submitted_brand:
                logo_path = current_logo
                
                # 確實將上傳的圖片二進位資料儲存到伺服器的 assets/ 資料夾中
                if uploaded_logo is not None:
                    try:
                        os.makedirs("assets", exist_ok=True)
                        logo_filename = f"{current_tenant_id}_{uploaded_logo.name}"
                        logo_path = os.path.join("assets", logo_filename)
                        with open(logo_path, "wb") as f:
                            f.write(uploaded_logo.getbuffer())
                    except Exception as file_err:
                        st.error(f"❌ 圖檔寫入伺服器硬碟失敗: {file_err}")

                # 寫入資料庫
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
                    
                    st.success("🎉 企業品牌識別與 Logo 已成功更新並寫入資料庫！")
                    st.rerun()
                except Exception as db_err:
                    st.error(f"❌ 資料庫儲存失敗: {db_err}")

    # ==========================================
    # 分頁二：AD 群組連結對應設定
    # ==========================================
    with tab_ad_mapping:
        st.markdown("#### 🔗 Active Directory (AD) 群組名稱與品牌連結管理")
        st.caption("在此建立 AD 群組名稱（例如 `CN=Reetech_Admins` 或 `CN=TayNinh_Branch`）與特定企業名稱、Logo 路徑的對應連結。當對應群組的使用者登入時，系統將自動套用該識別。")

        with st.form("ad_mapping_form"):
            ad_group_input = st.text_input("AD 群組名稱 (LDAP Distinguished Name / Group CN)")
            mapped_name_input = st.text_input("連結對應的企業名稱", value="裕豐電機工業 (西寧廠區)")
            mapped_sub_input = st.text_input("連結對應的副標題 / 越文名稱", value="CÔNG TY TNHH CN DỮ PHONG - TÂY NINH")
            
            ad_uploaded_logo = st.file_uploader("上傳此 AD 群組專屬 Logo 圖片", type=["png", "jpg", "jpeg"], key="ad_logo_uploader")

            submitted_ad = st.form_submit_button("➕ 儲存 AD 群組名稱連結規則", type="primary", use_container_width=True)

            if submitted_ad:
                if ad_group_input:
                    ad_logo_path = ""
                    if ad_uploaded_logo is not None:
                        try:
                            os.makedirs("assets", exist_ok=True)
                            safe_group_name = ad_group_input.replace('=', '_').replace(',', '_').replace(' ', '_')
                            ad_logo_path = os.path.join("assets", f"ad_mapped_{safe_group_name}_{ad_uploaded_logo.name}")
                            with open(ad_logo_path, "wb") as f:
                                f.write(ad_uploaded_logo.getbuffer())
                        except Exception as file_err:
                            st.warning(f"⚠️ AD 專屬圖檔寫入失敗: {file_err}")

                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO ad_group_branding_mapping (ad_group_name, mapped_company_name, mapped_subtitle, mapped_logo_url, updated_at)
                                VALUES (:group, :name, :sub, :lurl, CURRENT_TIMESTAMP)
                                ON CONFLICT (ad_group_name) 
                                DO UPDATE SET mapped_company_name = :name, mapped_subtitle = :sub, mapped_logo_url = :lurl, updated_at = CURRENT_TIMESTAMP
                            """), {
                                "group": ad_group_input,
                                "name": mapped_name_input,
                                "sub": mapped_sub_input,
                                "lurl": ad_logo_path
                            })
                        st.success(f"🎉 成功建立 AD 群組 [{ad_group_input}] 的品牌對應連結規則！")
                        st.rerun()
                    except Exception as db_err:
                        st.error(f"❌ 儲存 AD 對應規則失敗: {db_err}")
                else:
                    st.warning("⚠️ 請輸入有效的 AD 群組名稱。")

        # 呈現目前已設定的 AD 群組對應清單
        st.markdown("---")
        st.markdown("##### 📋 現有 AD 群組連結對應清單")
        try:
            with engine.connect() as conn:
                mappings = conn.execute(text("SELECT ad_group_name, mapped_company_name, mapped_subtitle, updated_at FROM ad_group_branding_mapping")).fetchall()
                if mappings:
                    for m in mappings:
                        st.info(f"**🔗 AD 群組:** `{m[0]}` ➡️ **企業名稱:** {m[1]} | **越文副標題:** {m[2]}")
                else:
                    st.info("💡 目前尚無設定任何 AD 群組連結規則（系統將預設採用手動設定之全域識別）。")
        except Exception:
            pass

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
