import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 商業 ERP 授權與全域動態設定模組多語系字典 (i18n)
# ----------------------------------------------------
LICENSING_I18N = {
    "繁體中文": {
        "title": "🔑 IT 系統管理與全域動態設定中心 (Admin Center)",
        "caption": "管理外部企業租戶合約、模組開關、系統 Storage 路徑，以及所有 API 憑證與資料庫動態設定。",
        "tab_tenants": "🏢 客戶租戶與授權總覽",
        "tab_add_tenant": "➕ 新增客戶租戶合約",
        "tab_manage_tenant": "⚙️ 編輯客戶模組權限",
        "tab_storage": "💾 系統 Storage 路徑",
        "tab_api_db": "🔌 API 串聯與資料庫動態設定",
        "table_header": "📋 全系統客戶租戶授權與模組開關清冊",
        "no_records": "目前尚無客戶租戶授權紀錄。",
        "col_index": "STT",
        "col_company": "客戶公司名稱",
        "col_tax": "統一編號 / 稅號",
        "col_plan": "授權方案",
        "col_seats": "席位數",
        "col_expiry": "合約到期日",
        "col_modules": "已啟用模組開關",
        "col_status": "狀態"
    },
    "Tiếng Việt": {
        "title": "🔑 Trung tâm Quản trị IT & Cấu hình Động",
        "caption": "Quản lý hợp đồng, đường dẫn Storage, cấu hình API và kết nối cơ sở dữ liệu.",
        "tab_tenants": "🏢 Tổng quan Khách hàng & Bản quyền",
        "tab_add_tenant": "➕ Thêm Khách hàng mới",
        "tab_manage_tenant": "⚙️ Chỉnh sửa Phân quyền",
        "tab_storage": "💾 Cấu hình Storage",
        "tab_api_db": "🔌 Cấu hình API & CSDL",
        "table_header": "📋 Danh sách khách hàng và module",
        "no_records": "Chưa có bản ghi khách hàng nào.",
        "col_index": "STT",
        "col_company": "Tên công ty",
        "col_tax": "Mã số thuế",
        "col_plan": "Gói cước",
        "col_seats": "Số ghế",
        "col_expiry": "Ngày hết hạn",
        "col_modules": "Module đang bật",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🔑 IT Administration & Dynamic Global Settings Center",
        "caption": "Manage enterprise tenants, cloud storage, API credentials, and database dynamic configurations.",
        "tab_tenants": "🏢 Tenants & Licensing Overview",
        "tab_add_tenant": "➕ Register New Tenant",
        "tab_manage_tenant": "⚙️ Edit Tenant Modules",
        "tab_storage": "💾 System Storage Path",
        "tab_api_db": "🔌 API & DB Dynamic Settings",
        "table_header": "📋 Enterprise Tenant License Matrix",
        "no_records": "No tenant license records found.",
        "col_index": "No.",
        "col_company": "Company Name",
        "col_tax": "Tax ID / MST",
        "col_plan": "Subscription Plan",
        "col_seats": "User Seats",
        "col_expiry": "Expiry Date",
        "col_modules": "Enabled Modules",
        "col_status": "Status"
    }
}

def init_system_settings_db(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.system_global_configs (
                    config_key VARCHAR(100) PRIMARY KEY,
                    config_value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))
    except Exception:
        pass

def render_system_licensing_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = LICENSING_I18N.get(active_lang, LICENSING_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    init_system_settings_db(engine)

    # 初始化資料庫 Session
    if "tenant_licensing_db" not in st.session_state or not isinstance(st.session_state.tenant_licensing_db, list):
        st.session_state.tenant_licensing_db = [
            {
                "tenant_id": "TENANT-001",
                "company_name": "裕豐電機工業 (Reetech Industrial)",
                "tax_id": "0312345678",
                "plan": "企業旗艦統包版 (Enterprise)",
                "max_seats": 50,
                "expiry_date": "2027-12-31",
                "modules": ["人事薪資", "倉庫資材", "工程報價與BOM", "電子發票與財務", "車輛門禁"],
                "status": "🟢 正常運行 (Active)"
            }
        ]

    if "system_storage_config" not in st.session_state:
        st.session_state.system_storage_config = {
            "storage_provider": "本地伺服器儲存 (Local NAS / Server)",
            "storage_path": "./storage_data/engineering_drawings/",
            "max_file_size_mb": 100.0,
            "auto_backup": True
        }

    tab_tenants, tab_add_tenant, tab_manage_tenant, tab_storage, tab_api_db = st.tabs([
        L["tab_tenants"], L["tab_add_tenant"], L["tab_manage_tenant"], L["tab_storage"], L["tab_api_db"]
    ])

    with tab_tenants:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.tenant_licensing_db:
            display_data = []
            for idx, tenant in enumerate(st.session_state.tenant_licensing_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    "客戶代碼": tenant["tenant_id"],
                    L["col_company"]: tenant["company_name"],
                    L["col_tax"]: tenant["tax_id"],
                    L["col_plan"]: tenant["plan"],
                    L["col_seats"]: f"{tenant['max_seats']} 席",
                    L["col_expiry"]: tenant["expiry_date"],
                    L["col_modules"]: ", ".join(tenant["modules"]),
                    L["col_status"]: tenant["status"]
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_add_tenant:
        st.markdown("### ➕ 註冊新企業客戶租戶與授權方案")
        with st.form("form_add_tenant_contract"):
            c1, c2 = st.columns(2)
            with c1:
                t_name = st.text_input("客戶公司名稱 (Company Name) *", value="Vietnam Power Engineering Corp")
                t_tax = st.text_input("統一編號 / 稅號 (Tax ID / MST)", value="0301122334")
                t_plan = st.selectbox("商業授權方案", ["基礎標準版 (Standard)", "進階製造版 (Advanced)", "企業旗艦統包版 (Enterprise)"])
            with c2:
                t_seats = st.number_input("最高授權使用者席位數 (Max Seats)", min_value=1, max_value=500, value=25)
                t_expiry = st.date_input("合約到期日 (Expiry Date)", value=datetime.date(2027, 12, 31))
                t_status = st.selectbox("合約狀態", ["🟢 正常運行 (Active)", "🟡 試用期 (Trial)", "🔴 授權到期 (Expired)"])

            st.markdown("---")
            st.markdown("##### 🧩 啟用模組功能開關 (Module Feature Flags)")
            m1, m2, m3 = st.columns(3)
            with m1:
                mod_hr = st.checkbox("👤 人事薪資與打卡考勤", value=True)
                mod_wh = st.checkbox("📦 倉庫庫存與資材管理", value=True)
            with m2:
                mod_eng = st.checkbox("⚡ 工程專案雙層報價與 BOM", value=True)
                mod_fin = st.checkbox("📊 財務應付帳款與電子發票", value=False)
            with m3:
                mod_veh = st.checkbox("🚗 廠區車輛維修與門禁保全", value=False)
                mod_app = st.checkbox("📋 跨部門電子簽核中心", value=True)

            if st.form_submit_button("🚀 建立新客戶租戶授權", type="primary", use_container_width=True):
                if t_name:
                    new_tenant_id = f"TENANT-{len(st.session_state.tenant_licensing_db)+1:03d}"
                    active_modules = []
                    if mod_hr: active_modules.append("人事薪資")
                    if mod_wh: active_modules.append("倉庫資材")
                    if mod_eng: active_modules.append("工程報價與BOM")
                    if mod_fin: active_modules.append("電子發票與財務")
                    if mod_veh: active_modules.append("車輛門禁")
                    if mod_app: active_modules.append("電子簽核")

                    st.session_state.tenant_licensing_db.append({
                        "tenant_id": new_tenant_id,
                        "company_name": t_name,
                        "tax_id": t_tax,
                        "plan": t_plan,
                        "max_seats": t_seats,
                        "expiry_date": str(t_expiry),
                        "modules": active_modules,
                        "status": t_status
                    })
                    st.success(f"🎉 成功建立新客戶租戶 [{t_name}]！")
                    st.rerun()

    with tab_manage_tenant:
        st.markdown("### ⚙️ 調整客戶租戶模組權限與到期日")
        if st.session_state.tenant_licensing_db:
            tenant_opts = [f"{t['tenant_id']} - {t['company_name']}" for t in st.session_state.tenant_licensing_db]
            sel_target_tenant = st.selectbox("選擇要調整的企業客戶", tenant_opts)
            target_tid = sel_target_tenant.split(" - ")[0]
            target_obj = next((t for t in st.session_state.tenant_licensing_db if t["tenant_id"] == target_tid), None)

            if target_obj:
                with st.form("form_edit_tenant"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        ed_name = st.text_input("客戶公司名稱", value=target_obj["company_name"])
                        ed_seats = st.number_input("最高授權席位數", min_value=1, max_value=500, value=target_obj["max_seats"])
                    with ec2:
                        ed_expiry = st.text_input("合約到期日 (YYYY-MM-DD)", value=target_obj["expiry_date"])
                        ed_status = st.selectbox("合約狀態", ["🟢 正常運行 (Active)", "🟡 試用期 (Trial)", "🔴 授權到期 (Expired)"])

                    if st.form_submit_button("💾 儲存客戶授權變更", type="primary", use_container_width=True):
                        target_obj["company_name"] = ed_name
                        target_obj["max_seats"] = ed_seats
                        target_obj["expiry_date"] = ed_expiry
                        target_obj["status"] = ed_status
                        st.success("🎉 客戶授權更新成功！")
                        st.rerun()

    with tab_storage:
        st.markdown("### 💾 系統雲端 Storage 儲存庫路徑與設定")
        with st.form("form_storage_settings"):
            cfg = st.session_state.system_storage_config
            s_provider = st.selectbox("儲存媒介類型", ["本地伺服器儲存 (Local NAS / Server)", "AWS S3 雲端儲存槽 (Cloud S3)", "Google Cloud Storage (GCS)"])
            s_path = st.text_input("Storage 實體掛載路徑或 Bucket 名稱", value=cfg["storage_path"])
            s_max_size = st.number_input("單一上傳檔案大小上限 (MB)", min_value=1.0, max_value=1000.0, value=cfg["max_file_size_mb"])

            if st.form_submit_button("💾 儲存 Storage 設定", type="primary", use_container_width=True):
                st.session_state.system_storage_config["storage_path"] = s_path
                st.success("🎉 Storage 路徑設定已成功更新！")

    # ----------------------------------------------------
    # 🔌 新增：API 串聯與資料庫動態設定分頁
    # ----------------------------------------------------
    with tab_api_db:
        st.markdown("### 🔌 API 串聯憑證與資料庫連線動態設定中心")
        st.info("💡 管理員專用：在此設定全系統所有外部 API（如 LINE Bot、Zalo、GDT 電子發票）的 Token 與資料庫連線字串，免改程式即可生效。")

        with st.form("form_global_api_db_settings"):
            st.markdown("##### 🔑 外部通訊與通知 API 設定")
            line_token = st.text_input("LINE Messaging API Access Token", value="YOUR_LINE_ACCESS_TOKEN_HERE", type="password")
            line_group = st.text_input("管理部 / 主管 LINE群組 ID 或 User ID", value="C123456789abcdef")
            zalo_token = st.text_input("Zalo OA / ZNS Access Token (選填)", value="", type="password")

            st.markdown("---")
            st.markdown("##### 🗄️ 資料庫與外部系統串聯參數")
            db_host = st.text_input("PostgreSQL 資料庫主機位址 (Host)", value="localhost")
            db_port = st.text_input("資料庫通訊埠 (Port)", value="5432")
            db_name = st.text_input("資料庫名稱 (Database Name)", value="postgres")
            gps_radius = st.number_input("工地外勤 GPS 有效打卡範圍 (公尺)", min_value=10, max_value=1000, value=100)

            if st.form_submit_button("💾 儲存所有 API 與系統連線設定", type="primary", use_container_width=True):
                if engine:
                    try:
                        with engine.begin() as conn:
                            configs = [
                                ("line_access_token", line_token),
                                ("manager_line_id", line_group),
                                ("zalo_access_token", zalo_token),
                                ("db_host", db_host),
                                ("db_port", db_port),
                                ("db_name", db_name),
                                ("gps_valid_radius", str(gps_radius))
                            ]
                            for k, v in configs:
                                conn.execute(text("""
                                    INSERT INTO public.system_global_configs (config_key, config_value, updated_at)
                                    VALUES (:k, :v, CURRENT_TIMESTAMP)
                                    ON CONFLICT (config_key) DO UPDATE 
                                    SET config_value = EXCLUDED.config_value, updated_at = CURRENT_TIMESTAMP;
                                """), {"k": k, "v": v})
                        st.success("🎉 所有 API 憑證與系統參數已成功寫入資料庫並即時生效！")
                    except Exception as e:
                        st.error(f"❌ 寫入資料庫失敗: {str(e)}")
                else:
                    st.success("🎉 [展示模式] API 與資料庫動態設定已成功儲存！")

# 兼容進入點
def show(engine=None, lang="繁體中文", **kwargs):
    render_system_licensing_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_system_licensing_page(engine=engine, lang=lang, **kwargs)

def render_system_licensing(*args, **kwargs):
    render_system_licensing_page(*args, **kwargs)

def render_licensing_control_page(*args, **kwargs):
    render_system_licensing_page(*args, **kwargs)
