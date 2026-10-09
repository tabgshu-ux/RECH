import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 商業 ERP 授權與多租戶管理模組多語系字典 (i18n)
# ----------------------------------------------------
LICENSING_I18N = {
    "繁體中文": {
        "title": "🔑 IT 商業授權中心 - 外部企業客戶與 ERP 模組授權控制台",
        "caption": "專為 SaaS / On-Premise 銷售設計：管理各外部企業租戶（Tenant）之合約方案、模組開關、到期日與使用者席位。",
        "tab_tenants": "🏢 客戶租戶與授權總覽",
        "tab_add_tenant": "➕ 新增客戶租戶合約",
        "tab_manage_tenant": "⚙️ 編輯客戶模組權限與到期日",
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
        "title": "🔑 Trung tâm Bản quyền Thương mại - Quản lý Khách hàng & Module ERP",
        "caption": "Dành cho kinh doanh phần mềm: Quản lý hợp đồng, bật/tắt module, hạn sử dụng và số lượng ghế của từng khách hàng doanh nghiệp.",
        "tab_tenants": "🏢 Tổng quan Khách hàng & Bản quyền",
        "tab_add_tenant": "➕ Thêm Khách hàng mới",
        "tab_manage_tenant": "⚙️ Chỉnh sửa Phân quyền & Hạn dùng",
        "table_header": "📋 Danh sách khách hàng và module đã kích hoạt",
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
        "title": "🔑 Commercial Licensing Center - Enterprise Tenant & Module Portal",
        "caption": "SaaS / On-Premise Sales Control: Manage tenant contracts, module feature flags, expiry dates, and user seat limits.",
        "tab_tenants": "🏢 Tenants & Licensing Overview",
        "tab_add_tenant": "➕ Register New Tenant Contract",
        "tab_manage_tenant": "⚙️ Edit Tenant Modules & Expiry",
        "table_header": "📋 Enterprise Tenant License & Module Matrix",
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

def render_system_licensing_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = LICENSING_I18N.get(active_lang, LICENSING_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 🏢 初始化多租戶客戶授權資料庫 (Tenant Licensing DB)
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
            },
            {
                "tenant_id": "TENANT-002",
                "company_name": "Công ty TNHH Xây lắp Tân Thuận",
                "tax_id": "0309876543",
                "plan": "基礎標準版 (Standard)",
                "max_seats": 15,
                "expiry_date": "2026-12-31",
                "modules": ["人事薪資", "倉庫資材"],
                "status": "🟡 試用期 (Trial)"
            }
        ]

    tab_tenants, tab_add_tenant, tab_manage_tenant = st.tabs([
        L["tab_tenants"], L["tab_add_tenant"], L["tab_manage_tenant"]
    ])

    with tab_tenants:
        st.markdown(f"### {L['table_header']}")
        st.info("💡 **銷售管理提示**：您可以隨時在此檢視各家購買系統的企業客戶合約狀態與模組開通清單。")
        
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
                    
                    # 收集勾選的模組
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
                    st.success(f"🎉 成功建立新客戶租戶 [{t_name}]！代碼：`{new_tenant_id}`")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫客戶公司名稱！")

    with tab_manage_tenant:
        st.markdown("### ⚙️ 調整客戶租戶模組權限、到期日與席位")
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
                        ed_plan = st.selectbox("授權方案", ["基礎標準版 (Standard)", "進階製造版 (Advanced)", "企業旗艦統包版 (Enterprise)"], index=0 if "標準" in target_obj["plan"] else (1 if "進階" in target_obj["plan"] else 2))
                        ed_seats = st.number_input("最高授權席位數", min_value=1, max_value=500, value=target_obj["max_seats"])
                    with ec2:
                        ed_expiry = st.text_input("合約到期日 (YYYY-MM-DD)", value=target_obj["expiry_date"])
                        status_list = ["🟢 正常運行 (Active)", "🟡 試用期 (Trial)", "🔴 授權到期 (Expired)"]
                        ed_status = st.selectbox("合約狀態", status_list, index=0 if "正常" in target_obj["status"] else (1 if "試用" in target_obj["status"] else 2))

                    st.markdown("---")
                    st.markdown("##### 🧩 調整模組啟用開關")
                    current_mods = target_obj["modules"]
                    ed_mod_hr = st.checkbox("👤 人事薪資與打卡考勤", value="人事薪資" in current_mods)
                    ed_mod_wh = st.checkbox("📦 倉庫庫存與資材管理", value="倉庫資材" in current_mods)
                    ed_mod_eng = st.checkbox("⚡ 工程專案雙層報價與 BOM", value="工程報價與BOM" in current_mods)
                    ed_mod_fin = st.checkbox("📊 財務應付帳款與電子發票", value="電子發票與財務" in current_mods)
                    ed_mod_veh = st.checkbox("🚗 廠區車輛維修與門禁保全", value="車輛門禁" in current_mods)
                    ed_mod_app = st.checkbox("📋 跨部門電子簽核中心", value="電子簽核" in current_mods)

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        save_btn = st.form_submit_button("💾 儲存客戶授權變更", type="primary", use_container_width=True)
                    with col_b2:
                        del_btn = st.form_submit_button("🔥 終止並刪除此客戶合約", type="secondary", use_container_width=True)

                    if save_btn:
                        updated_mods = []
                        if ed_mod_hr: updated_mods.append("人事薪資")
                        if ed_mod_wh: updated_mods.append("倉庫資材")
                        if ed_mod_eng: updated_mods.append("工程報價與BOM")
                        if ed_mod_fin: updated_mods.append("電子發票與財務")
                        if ed_mod_veh: updated_mods.append("車輛門禁")
                        if ed_mod_app: updated_mods.append("電子簽核")

                        target_obj["company_name"] = ed_name
                        target_obj["plan"] = ed_plan
                        target_obj["max_seats"] = ed_seats
                        target_obj["expiry_date"] = ed_expiry
                        target_obj["status"] = ed_status
                        target_obj["modules"] = updated_mods
                        st.success(f"🎉 客戶 [{ed_name}] 的授權方案與模組開關已成功更新！")
                        st.rerun()

                    if del_btn:
                        st.session_state.tenant_licensing_db = [t for t in st.session_state.tenant_licensing_db if t["tenant_id"] != target_tid]
                        st.success(f"🗑️ 客戶租戶 [{target_tid}] 合約已終止並自系統中移除！")
                        st.rerun()
        else:
            st.info("目前尚無客戶租戶可供修改。")

def show(lang="繁體中文", **kwargs):
    render_system_licensing_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_system_licensing_page(lang, **kwargs)

def render_system_licensing(*args, **kwargs):
    render_system_licensing_page(*args, **kwargs)
