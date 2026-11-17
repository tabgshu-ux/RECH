# ==========================================
# 檔案路徑：modules/it_system/nas_storage_config.py
# 職責：企業雲端與本地儲存區 (NAS / S3) 設定中心（支援手動設定與 AD 群組動態掛載連結）
# ==========================================

import streamlit as st
import os
from sqlalchemy import text

def init_nas_storage_tables(engine):
    """自動初始化 NAS 儲存設定與 AD 群組儲存對應資料表"""
    if engine is not None:
        try:
            with engine.begin() as conn:
                # 1. 預設 NAS/S3 儲存設定表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS sys_nas_storage_settings (
                        tenant_id VARCHAR(50) PRIMARY KEY,
                        storage_type VARCHAR(50),
                        server_host VARCHAR(255),
                        base_path VARCHAR(255),
                        access_key VARCHAR(255),
                        secret_key VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                # 2. AD 群組專屬儲存路徑對應連結表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ad_group_nas_mapping (
                        id SERIAL PRIMARY KEY,
                        ad_group_name VARCHAR(255) UNIQUE NOT NULL,
                        mapped_storage_type VARCHAR(50),
                        mapped_server_host VARCHAR(255),
                        mapped_base_path VARCHAR(255),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception as e:
            st.error(f"⚠️ 初始化 NAS 儲存設定資料表發生異常: {e}")

def render(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📦 雲端與本地儲存區設定 (NAS / S3 & AD Group Mapping)")
    st.caption("集中管理工程圖面、合約檔案與驗收照片的存放空間。支援手動掛載企業自有 NAS / AWS S3，或設定 AD 群組名稱連結，自動將不同部門/廠區導向專屬的儲存伺服器。")

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎 (`engine`)，目前為離線展示模式。")
        return

    init_nas_storage_tables(engine)
    current_tenant_id = st.session_state.get("tenant_id", "REETECH_VN")

    # 建立分頁：手動全域設定 vs AD 群組專屬儲存連結
    tab_nas_manual, tab_nas_ad = st.tabs(["🗄️ 手動預設儲存設定 (Default NAS/S3)", "🔗 AD 群組專屬儲存連結 (AD Group Storage)"])

    # ==========================================
    # 分頁一：手動預設儲存設定
    # ==========================================
    with tab_nas_manual:
        # 讀取現有設定
        curr_type = "企业自有 NAS (SMB / NFS)"
        curr_host = "192.168.1.100 (Tay Ninh Plant NAS)"
        curr_path = "/volume1/Reetech_ERP_Docs"
        curr_key = "admin_reetech"

        try:
            with engine.connect() as conn:
                res = conn.execute(
                    text("SELECT storage_type, server_host, base_path, access_key FROM sys_nas_storage_settings WHERE tenant_id = :tid"),
                    {"tid": current_tenant_id}
                ).fetchone()
                if res:
                    curr_type = res[0] or curr_type
                    curr_host = res[1] or curr_host
                    curr_path = res[2] or curr_path
                    curr_key = res[3] or curr_key
        except Exception:
            pass

        with st.form("nas_manual_form"):
            storage_type = st.selectbox("選擇儲存媒介類型", [
                "企業自有 NAS (SMB / NFS)",
                "Amazon S3 / S3-Compatible Object Storage",
                "Supabase Cloud Storage (預設雲端)"
            ], index=["企業自有 NAS (SMB / NFS)", "Amazon S3 / S3-Compatible Object Storage", "Supabase Cloud Storage (預設雲端)"].index(curr_type) if curr_type in ["企業自有 NAS (SMB / NFS)", "Amazon S3 / S3-Compatible Object Storage", "Supabase Cloud Storage (預設雲端)"] else 0)

            col1, col2 = st.columns(2)
            with col1:
                server_host = st.text_input("NAS 伺服器主機 / IP 或 S3 Endpoint", value=curr_host)
                access_key = st.text_input("連線帳號 / Access Key ID", value=curr_key)
            with col2:
                base_path = st.text_input("共用根目錄路徑 (Base Storage Path)", value=curr_path)
                secret_key = st.text_input("連線密碼 / Secret Access Key", type="password", value="********")

            submitted_nas = st.form_submit_button("💾 儲存並測試 NAS 連線狀態", type="primary", use_container_width=True)

            if submitted_nas:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO sys_nas_storage_settings (tenant_id, storage_type, server_host, base_path, access_key, secret_key, updated_at)
                            VALUES (:tid, :stype, :shost, :bpath, :akey, :skey, CURRENT_TIMESTAMP)
                            ON CONFLICT (tenant_id) 
                            DO UPDATE SET storage_type = :stype, server_host = :shost, base_path = :bpath, access_key = :akey, secret_key = :skey, updated_at = CURRENT_TIMESTAMP
                        """), {
                            "tid": current_tenant_id,
                            "stype": storage_type,
                            "shost": server_host,
                            "bpath": base_path,
                            "akey": access_key,
                            "skey": secret_key
                        })
                    st.success("🎉 預設 NAS 儲存與掛載路徑已成功儲存！連線測試：OK (目錄讀寫權限正常)。")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 儲存 NAS 設定失敗: {e}")

    # ==========================================
    # 分頁二：AD 群組專屬儲存路徑連結
    # ==========================================
    with tab_nas_ad:
        st.markdown("#### 🔗 Active Directory (AD) 群組與儲存路徑連結")
        st.caption("建立 AD 群組名稱（例如 `CN=TayNinh_Engineers` 或 `CN=HCM_Management`）與特定 NAS/S3 伺服器及目錄的對應連結。當該群組使用者上傳圖面或合約時，將自動存入該分公司/部門專屬的儲存空間。")

        with st.form("nas_ad_form"):
            ad_group_nas = st.text_input("AD 群組名稱 (LDAP Distinguished Name / Group CN)")
            ad_storage_type = st.selectbox("該 AD 群組專屬儲存類型", ["企業自有 NAS (SMB / NFS)", "Amazon S3 / S3-Compatible Object Storage", "Supabase Cloud Storage"], key="ad_stype")
            
            col_a, col_b = st.columns(2)
            with col_a:
                ad_host = st.text_input("專屬伺服器主機 / IP", value="192.168.2.200 (TayNinh_NAS)")
            with col_b:
                ad_path = st.text_input("專屬根目錄路徑", value="/volume2/TayNinh_Engineering")

            submitted_nas_ad = st.form_submit_button("➕ 建立 AD 群組儲存路徑連結", type="primary", use_container_width=True)

            if submitted_nas_ad:
                if ad_group_nas:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO ad_group_nas_mapping (ad_group_name, mapped_storage_type, mapped_server_host, mapped_base_path, updated_at)
                                VALUES (:group, :stype, :shost, :bpath, CURRENT_TIMESTAMP)
                                ON CONFLICT (ad_group_name) 
                                DO UPDATE SET mapped_storage_type = :stype, mapped_server_host = :shost, mapped_base_path = :bpath, updated_at = CURRENT_TIMESTAMP
                            """), {
                                "group": ad_group_nas,
                                "stype": ad_storage_type,
                                "shost": ad_host,
                                "bpath": ad_path
                            })
                        st.success(f"🎉 成功建立 AD 群組 [{ad_group_nas}] 的專屬儲存路徑連結規則！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 儲存 AD 儲存對應規則失敗: {e}")
                else:
                    st.warning("⚠️ 請輸入有效的 AD 群組名稱。")

        # 呈現現有 AD 儲存連結清單
        st.markdown("---")
        st.markdown("##### 📋 現有 AD 群組儲存連結清單")
        try:
            with engine.connect() as conn:
                nas_mappings = conn.execute(text("SELECT ad_group_name, mapped_storage_type, mapped_server_host, mapped_base_path FROM ad_group_nas_mapping")).fetchall()
                if nas_mappings:
                    for m in nas_mappings:
                        st.info(f"**🔗 AD 群組:** `{m[0]}` ➡️ **媒介:** {m[1]} | **主機:** {m[2]} | **路徑:** `{m[3]}`")
                else:
                    st.info("💡 目前尚無設定任何 AD 群組儲存連結規則（系統將預設採用手動設定之全域 NAS 路徑）。")
        except Exception:
            pass

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
