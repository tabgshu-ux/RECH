import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 系統授權與模組控制模組多語系字典 (i18n)
# ----------------------------------------------------
LICENSING_I18N = {
    "繁體中文": {
        "title": "🔑 IT 管理中心 - 跨國 ERP 模組授權與訂閱控制",
        "caption": "管理裕豐電機工業（Reetech Industrial）各海外廠區（西寧廠、海防廠）與台灣總部之 ERP 模組授權狀態。",
        "tab_status": "📊 授權狀態總覽與有效期限",
        "tab_config": "⚙ 模組授權開關與期限調整",
        "tab_add_mod": "➕ 新增系統模組授權",
        "tab_manage_mod": "✏️ 修改與刪除模組授權",
        "status_header": "📋 系統核心模組授權清冊",
        "no_records": "目前無授權模組資料。",
        "config_header": "⚙️ 調整模組授權與使用期限",
        "lbl_module": "選擇要調整的模組 *",
        "lbl_status": "授權啟用狀態 *",
        "status_opts": ["啟用 (Active)", "停用 (Suspended)", "試用期 (Trial)"],
        "lbl_expiry": "授權到期日 *",
        "btn_save": "💾 儲存並更新授權設定",
        "success_save": "✅ 模組 `{module_name}` 授權設定已成功更新！",
        "col_index": "STT",
        "col_code": "模組代碼",
        "col_name": "模組名稱",
        "col_ver": "版本",
        "col_expiry": "到期日",
        "col_status": "授權狀態"
    },
    "Tiếng Việt": {
        "title": "🔑 Quản trị IT - Quản lý Bản quyền & Kích hoạt Module ERP",
        "caption": "Quản lý trạng thái bản quyền các module ERP cho nhà máy Tây Ninh, Hải Phòng và Trụ sở chính Đài Loan.",
        "tab_status": "📊 Tổng quan Bản quyền & Thời hạn",
        "tab_config": "⚙️ Cấu hình Kích hoạt & Hạn mức",
        "tab_add_mod": "➕ Thêm Module mới",
        "tab_manage_mod": "✏️ Sửa & Xóa Module",
        "status_header": "📋 Danh sách Bản quyền Module Hệ thống",
        "no_records": "Hiện không có bản ghi bản quyền nào.",
        "config_header": "⚙️ Điều chỉnh trạng thái bản quyền module",
        "lbl_module": "Chọn module cần cấu hình *",
        "lbl_status": "Trạng thái bản quyền *",
        "status_opts": ["Đã kích hoạt (Active)", "Tạm ngưng (Suspended)", "Dùng thử (Trial)"],
        "lbl_expiry": "Ngày hết hạn *",
        "btn_save": "💾 Lưu và cập nhật bản quyền",
        "success_save": "✅ Đã cập nhật thành công bản quyền cho module `{module_name}`!",
        "col_index": "STT",
        "col_code": "Mã module",
        "col_name": "Tên module",
        "col_ver": "Phiên bản",
        "col_expiry": "Ngày hết hạn",
        "col_status": "Trạng thái"
    },
    "English": {
        "title": "🔑 IT Center - ERP Module Licensing & Subscription Control",
        "caption": "Manage ERP module licensing status for overseas plants (Tay Ninh, Hai Phong) and Taiwan HQ.",
        "tab_status": "📊 Licensing Overview & Expiry",
        "tab_config": "⚙️ Module Switches & Quota Adjustments",
        "tab_add_mod": "➕ Add New Module",
        "tab_manage_mod": "✏️ Edit & Delete Module",
        "status_header": "📋 System Core Module Licenses",
        "no_records": "No license records found.",
        "config_header": "⚙️ Adjust Module License & Expiry Date",
        "lbl_module": "Select Module to Configure *",
        "lbl_status": "License Status *",
        "status_opts": ["Active", "Suspended", "Trial"],
        "lbl_expiry": "License Expiry Date *",
        "btn_save": "💾 Save & Update License",
        "success_save": "✅ License for module `{module_name}` updated successfully!",
        "col_index": "No.",
        "col_code": "Module Code",
        "col_name": "Module Name",
        "col_ver": "Version",
        "col_expiry": "Expiry Date",
        "col_status": "Status"
    }
}

# ----------------------------------------------------
# 🔄 授權模組專用：中越英智慧語意對照引擎
# ----------------------------------------------------
def smart_translate_license(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()
    if "啟用" in text_val or "active" in val_lower or "kích hoạt" in val_lower:
        if target_lang == "Tiếng Việt": return "🟢 Đã kích hoạt (Active)"
        elif target_lang == "English": return "🟢 Active"
        return "🟢 授權啟用 (Active)"
    elif "停用" in text_val or "suspended" in val_lower:
        if target_lang == "Tiếng Việt": return "🔴 Tạm ngưng (Suspended)"
        elif target_lang == "English": return "🔴 Suspended"
        return "🔴 授權停用 (Suspended)"
    elif "試用" in text_val or "trial" in val_lower:
        if target_lang == "Tiếng Việt": return "🟡 Dùng thử (Trial)"
        elif target_lang == "English": return "🟡 Trial"
        return "🟡 試用期 (Trial)"

    return text_val

def render_system_licensing_page(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = LICENSING_I18N.get(active_lang, LICENSING_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化模組授權資料庫
    if "system_licenses_db" not in st.session_state or not isinstance(st.session_state.system_licenses_db, list):
        st.session_state.system_licenses_db = [
            {"code": "MOD-HR", "name": "人事薪資與打卡考勤管理", "version": "v3.5", "expiry": "2027-12-31", "status": "啟用"},
            {"code": "MOD-FIN", "name": "財務 AP 應付帳款與電子發票", "version": "v4.0", "expiry": "2027-12-31", "status": "啟用"},
            {"code": "MOD-WH", "name": "倉庫庫存與資材條碼管理", "version": "v3.8", "expiry": "2027-12-31", "status": "啟用"},
            {"code": "MOD-VEH", "name": "廠區車輛維修與門禁保全", "version": "v2.5", "expiry": "2027-12-31", "status": "啟用"},
            {"code": "MOD-APP", "name": "跨部門電子簽核中心", "version": "v4.2", "expiry": "2027-12-31", "status": "啟用"},
        ]

    tab_status, tab_config, tab_add_mod, tab_manage_mod = st.tabs([
        L["tab_status"], L["tab_config"], L["tab_add_mod"], L["tab_manage_mod"]
    ])

    with tab_status:
        st.markdown(f"### {L['status_header']}")
        if st.session_state.system_licenses_db:
            display_data = []
            for idx, item in enumerate(st.session_state.system_licenses_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_ver"]: item["version"],
                    L["col_expiry"]: item["expiry"],
                    L["col_status"]: smart_translate_license(item["status"], active_lang)
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)
        else:
            st.info(L["no_records"])

    with tab_config:
        st.markdown(f"### {L['config_header']}")
        with st.form("form_licensing_config"):
            module_opts = {item["name"]: item["code"] for item in st.session_state.system_licenses_db}
            selected_mod_name = st.selectbox(L["lbl_module"], list(module_opts.keys()))
            new_status = st.selectbox(L["lbl_status"], L["status_opts"])
            new_expiry = st.date_input(L["lbl_expiry"], value=datetime.date(2027, 12, 31))

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                target_code = module_opts[selected_mod_name]
                for item in st.session_state.system_licenses_db:
                    if item["code"] == target_code:
                        if "啟用" in new_status or "Active" in new_status or "kích hoạt" in new_status:
                            item["status"] = "啟用"
                        elif "停用" in new_status or "Suspended" in new_status or "Tạm ngưng" in new_status:
                            item["status"] = "停用"
                        else:
                            item["status"] = "試用期"
                        item["expiry"] = new_expiry.strftime("%Y-%m-%d")
                st.success(L["success_save"].format(module_name=selected_mod_name))
                st.rerun()

    with tab_add_mod:
        st.markdown("### ➕ 註冊與新增系統 ERP 模組授權")
        with st.form("form_add_new_module"):
            ac1, ac2 = st.columns(2)
            with ac1:
                new_code = st.text_input("模組代碼 (例如: MOD-ENG) *", value="MOD-ENG")
                new_name = st.text_input("模組名稱 *", value="工程與專案管理模組")
            with ac2:
                new_ver = st.text_input("版本號", value="v1.0")
                new_exp = st.date_input("授權到期日", value=datetime.date(2027, 12, 31))
            
            add_status = st.selectbox("初始授權狀態", ["啟用", "停用", "試用期"])

            if st.form_submit_button("🚀 建立新模組授權", type="primary", use_container_width=True):
                if new_code and new_name:
                    existing_codes = [m["code"] for m in st.session_state.system_licenses_db]
                    if new_code in existing_codes:
                        st.error(f"⚠️ 錯誤：模組代碼 `{new_code}` 已經存在！")
                    else:
                        st.session_state.system_licenses_db.append({
                            "code": new_code,
                            "name": new_name,
                            "version": new_ver,
                            "expiry": str(new_exp),
                            "status": add_status
                        })
                        st.success(f"✅ 成功新增模組授權 [{new_name}] ({new_code})！")
                        st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫模組代碼與模組名稱！")

    with tab_manage_mod:
        st.markdown("### ✏️ 修改與刪除現有模組授權")
        if st.session_state.system_licenses_db:
            mod_options = [f"{m['code']} - {m['name']}" for m in st.session_state.system_licenses_db]
            sel_mod_target = st.selectbox("選擇要修改或刪除的模組授權", mod_options)
            target_mcode = sel_mod_target.split(" - ")[0]
            target_mod_obj = next((m for m in st.session_state.system_licenses_db if m["code"] == target_mcode), None)

            if target_mod_obj:
                with st.form("form_edit_module_license"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        ed_m_name = st.text_input("模組名稱", value=target_mod_obj["name"])
                        ed_m_ver = st.text_input("版本", value=target_mod_obj["version"])
                    with ec2:
                        status_list = ["啟用", "停用", "試用期"]
                        current_status_idx = status_list.index(target_mod_obj["status"]) if target_mod_obj["status"] in status_list else 0
                        ed_m_status = st.selectbox("授權狀態", status_list, index=current_status_idx)
                        ed_m_expiry = st.text_input("到期日 (YYYY-MM-DD)", value=target_mod_obj["expiry"])

                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        update_mod_btn = st.form_submit_button("💾 儲存模組變更", type="primary", use_container_width=True)
                    with col_b2:
                        delete_mod_btn = st.form_submit_button("🔥 刪除此模組授權", type="secondary", use_container_width=True)

                    if update_mod_btn:
                        target_mod_obj["name"] = ed_m_name
                        target_mod_obj["version"] = ed_m_ver
                        target_mod_obj["status"] = ed_m_status
                        target_mod_obj["expiry"] = ed_m_expiry
                        st.success(f"🎉 模組 [{target_mcode}] 授權資料已成功更新！")
                        st.rerun()

                    if delete_mod_btn:
                        st.session_state.system_licenses_db = [m for m in st.session_state.system_licenses_db if m["code"] != target_mcode]
                        st.success(f"🗑️ 模組 [{target_mcode}] 已從系統授權清單中移除！")
                        st.rerun()
        else:
            st.info("目前尚無模組授權可供修改。")

def show(lang="繁體中文", **kwargs):
    render_system_licensing_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_system_licensing_page(lang, **kwargs)

def render_system_licensing(*args, **kwargs):
    render_system_licensing_page(*args, **kwargs)
