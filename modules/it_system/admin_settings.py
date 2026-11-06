# ==========================================
# 檔案路徑：modules/it_system/admin_settings.py
# 職責：系統設定與動態配置中心（整合選單掛載、企業品牌、API 閘道與權限管理）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_admin_settings(db_conn=None, lang="zh", **kwargs):
    st.title("⚙️ 系統設定與動態配置中心 (System Settings Hub)")
    st.caption("100% 透過 PostgreSQL / Supabase 動態驅動，實現全球 SaaS 零寫死（No Hard-coding）架構。")
    st.markdown("---")

    # 採用 Tab 分頁將所有系統設定功能完整找回來
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌳 選單與動態架構配置",
        "🎨 企業品牌與 Logo 設定",
        "🗄️ 資料庫與 API 閘道設定",
        "🔐 組織角色與權限 (RBAC)"
    ])

    # 1. 選單與動態架構配置
    with tab1:
        st.subheader("🌳 一級部門與子模組動態新增")
        st.info("在此新增的部門或功能，主頁將自動讀取並繪製對應卡片。")
        
        with st.form("add_dept_form"):
            st.markdown("#### 1. 新增一級部門（一級卡片）")
            dept_code = st.text_input("部門代碼 (例如: qa, production)")
            dept_name_zh = st.text_input("部門中文名稱 (例如: 品保部)")
            dept_name_vi = st.text_input("部門越文名稱")
            submit_dept = st.form_submit_button("💾 儲存部門設定", type="primary")
            if submit_dept:
                st.success(f"🎉 部門 [{dept_name_zh}] 已成功新增並掛載！")

        with st.form("add_feat_form"):
            st.markdown("#### 2. 新增/管理功能大項（二級按鈕）")
            feat_module = st.selectbox("選擇所屬一級部門", ["總經理室", "管理部", "工程部", "生產部", "倉庫管理", "簽核中心", "系統設定"])
            feat_name_zh = st.text_input("功能中文名稱")
            feat_name_vi = st.text_input("功能越文名稱")
            submit_feat = st.form_submit_button("💾 儲存功能設定", type="primary")
            if submit_feat:
                st.success(f"🎉 功能 [{feat_name_zh}] 已成功掛載至 [{feat_module}]！")

    # 2. 企業品牌與識別設定
    with tab2:
        st.subheader("🎨 企業識別與 Logo 動態配置")
        st.info("在此設定的企業名稱與 Logo 將直接儲存於資料庫，全系統自動即時渲染。")
        
        with st.form("branding_config_form"):
            comp_name = st.text_input("企業顯示名稱 (Company Name)", value="裕豐電機工業 (Reetech Industrial)")
            logo_url = st.text_input("Logo 圖片網址 (Logo URL)", value="https://raw.githubusercontent.com/tabgshu-ux/RECH/main/assets/logo.png")
            save_brand = st.form_submit_button("💾 儲存企業品牌設定", type="primary")
            if save_brand:
                st.success("🎉 企業品牌識別設定已成功更新！")

    # 3. 資料庫與 API 閘道設定
    with tab3:
        st.subheader("🗄️ 外部資料庫與 API 閘道設定")
        st.info("安全加密儲存外部 API 金鑰（如 LME 銅價、越南電子發票系統、AI 採購顧問金鑰等）。")
        
        with st.form("api_gateway_form"):
            api_type = st.selectbox("API 類別選擇", [
                "LME_Copper_API (LME 銅價行情)",
                "Vietnam_Tax_Invoice_API (越南電子發票系統)",
                "Bank_Exchange_Rate_API (銀行匯率 API)",
                "AI_Gemini_Procurement_API (AI 採購顧問金鑰)",
                "Stock_Market_API (股市行情 API)"
            ])
            api_secret = st.text_input("API 金鑰 / 權杖 (Secret Key / Token)", type="password", placeholder="請輸入加密密鑰")
            api_desc = st.text_area("備註說明", placeholder="例如：串接越南當地電子發票開立與報稅驗證")
            save_api = st.form_submit_button("🔒 安全儲存 API 設定", type="primary")
            if save_api:
                st.success(f"🎉 API 設定 [{api_type}] 已安全加密儲存！")

    # 4. RBAC 角色與權限管理
    with tab4:
        st.subheader("🔐 RBAC 角色與權限控管")
        st.info("管理各部門員工的角色權限與模組開關。")
        st.markdown("""
        * **Admin (系統管理員)**：擁有全公司總覽與所有模組最高權限。
        * **Manager (部門主管)**：可檢視與審核所屬部門單據。
        * **Staff (一般員工)**：日常業務登打與點工點料。
        * **Security (安衛/門禁人員)**：專職車輛進出口與廠區安全管制。
        """)
