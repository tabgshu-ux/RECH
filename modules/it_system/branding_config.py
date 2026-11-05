import streamlit as st
from sqlalchemy import text

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🎨 企業品牌與識別設定 (Tenant Branding & Logo Management)")
    st.caption("多租戶白標設定：在此變更公司名稱、副標題與上傳企業專屬 Logo，系統將自動套用至全站側邊欄。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎 (`engine`)，目前為離線展示模式。")
        return

    current_tenant_id = st.session_state.get("tenant_id", "REETECH_VN")

    # 讀取現有品牌設定
    try:
        with engine.connect() as conn:
            res = conn.execute(
                text("SELECT company_name, company_subtitle, logo_url FROM tenant_settings WHERE tenant_id = :tid"),
                {"tid": current_tenant_id}
            ).fetchone()
            current_name = res[0] if res else "裕豐電機工業有限公司"
            current_sub = res[1] if res else "CÔNG TY TNHH CN DỮ PHONG"
            current_logo = res[2] if res else ""
    except Exception:
        current_name = st.session_state.get("tenant_company_name", "裕豐電機工業有限公司")
        current_sub = st.session_state.get("tenant_company_sub", "CÔNG TY TNHH CN DỮ PHONG")
        current_logo = ""

    with st.form("branding_form"):
        new_company_name = st.text_input("企業正式名稱 (Company Name)", value=current_name)
        new_company_sub = st.text_input("企業副標題 / 越文名稱 (Subtitle / Local Name)", value=current_sub)
        
        uploaded_logo = st.file_uploader("上傳企業 Logo 圖片 (建議尺寸 200x60px, PNG/JPG)", type=["png", "jpg", "jpeg"])
        
        submitted_brand = st.form_submit_button("💾 儲存並即時更新企業識別 (Save Branding)")
        if submitted_brand:
            logo_path = current_logo
            if uploaded_logo is not None:
                logo_path = f"assets/{current_tenant_id}_{uploaded_logo.name}"
            
            try:
                with engine.begin() as conn:
                    upsert_sql = text("""
                        INSERT INTO tenant_settings (tenant_id, company_name, company_subtitle, logo_url)
                        VALUES (:tid, :cname, :csub, :lurl)
                        ON CONFLICT (tenant_id) 
                        DO UPDATE SET company_name = :cname, company_subtitle = :csub, logo_url = :lurl, updated_at = CURRENT_TIMESTAMP
                    """)
                    conn.execute(upsert_sql, {
                        "tid": current_tenant_id,
                        "cname": new_company_name,
                        "csub": new_company_sub,
                        "lurl": logo_path
                    })
                
                st.session_state.tenant_company_name = new_company_name
                st.session_state.tenant_company_sub = new_company_sub
                st.session_state.tenant_logo_url = logo_path
                
                st.success("🎉 企業品牌識別更新成功！側邊欄與標題已同步動態刷新。")
                st.rerun()
            except Exception as e:
                st.session_state.tenant_company_name = new_company_name
                st.session_state.tenant_company_sub = new_company_sub
                st.success("🎉 企業識別已暫存至當前工作階段！")
                st.rerun()
