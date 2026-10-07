import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 合約管理模組多語系字典 (i18n)
# ----------------------------------------------------
CONTRACT_I18N = {
    "繁體中文": {
        "title": "✍️ 管理部 - 企業合約管理與主管審查中心",
        "caption": "管理裕豐電機工業各項工程合約、設備採購合約與租賃合約，支援線上即時修改、合約狀態追蹤及舊合約檔案上傳供主管審查。",
        "tab_list": "📑 合約清冊與線上即時編輯",
        "tab_add": "➕ 新增合約登記",
        "tab_upload": "📤 上傳舊合約與附件（主管審查）",
        "table_header": "📋 裕豐電機工業現行合約總覽",
        "no_records": "目前無合約紀錄。",
        "edit_header": "✏️ 線上修改合約資料",
        "select_contract": "選擇要修改的合約 *",
        "btn_update": "💾 儲存修改內容",
        "success_update": "✅ 合約 `{code}` 資料已成功更新！",
        "add_header": "➕ 登記全新合約",
        "lbl_code": "合約編號 *",
        "lbl_name": "合約名稱 / 專案主題 *",
        "lbl_party": "簽約對方 (客戶/供應商) *",
        "party_placeholder": "例如: 越南和鼎隆建築責任有限公司",
        "lbl_type": "合約類型 *",
        "type_opts": ["工程承攬合約", "設備採購合約", "土地與廠房租賃", "委任與技術服務合約"],
        "lbl_amount": "合約總金額 (VND) *",
        "lbl_date": "簽約生效日期 *",
        "lbl_status": "合約狀態 *",
        "status_opts": ["進行中 (Active)", "已驗收結案 (Closed)", "暫停中 (Suspended)", "審核中 (Reviewing)"],
        "btn_save": "💾 建立合約檔案",
        "success_save": "✅ 合約 `{code}` 已成功建立！",
        "fill_warning": "⚠️ 請完整填寫合約編號、名稱與簽約對象！",
        "upload_header": "📤 上傳舊合約掃描檔 / Word / PDF 供主管審查",
        "select_upload_contract": "選擇對應的合約專案 *",
        "lbl_file": "選擇合約檔案 (.pdf, .doc, .docx, .xls)",
        "btn_upload_file": "🚀 確認上傳合約檔案",
        "success_upload": "✅ 檔案 `{filename}` 已成功上傳並歸檔至專案合約！",
        # 表格欄位
        "col_index": "STT",
        "col_code": "合約編號",
        "col_name": "合約名稱",
        "col_party": "簽約對象",
        "col_type": "類型",
        "col_amount": "合約金額 (VND)",
        "col_date": "簽約日期",
        "col_status": "狀態",
        "col_file": "合約附件"
    },
    "Tiếng Việt": {
        "title": "✍️ Khối Hành chính - Quản lý Hợp đồng & Phê duyệt của Quản lý",
        "caption": "Quản lý hợp đồng xây dựng, mua sắm thiết bị và cho thuê; hỗ trợ chỉnh sửa trực tuyến và tải lên hợp đồng cũ để kiểm tra.",
        "tab_list": "📑 Danh sách Hợp đồng & Chỉnh sửa",
        "tab_add": "➕ Đăng ký Hợp đồng Mới",
        "tab_upload": "📤 Tải lên Hợp đồng Cũ (Dành cho Quản lý)",
        "table_header": "📋 Tổng quan Hợp đồng hiện hành",
        "no_records": "Hiện không có bản ghi hợp đồng nào.",
        "edit_header": "✏️ Chỉnh sửa thông tin hợp đồng",
        "select_contract": "Chọn hợp đồng cần sửa *",
        "btn_update": "💾 Lưu thay đổi",
        "success_update": "✅ Đã cập nhật thành công hợp đồng `{code}`!",
        "add_header": "➕ Đăng ký hợp đồng mới",
        "lbl_code": "Mã hợp đồng *",
        "lbl_name": "Tên hợp đồng / Dự án *",
        "lbl_party": "Đối tác ký kết *",
        "party_placeholder": "Ví dụ: CÔNG TY TNHH XÂY DỰNG HO TEAM",
        "lbl_type": "Loại hợp đồng *",
        "type_opts": ["Hợp đồng xây dựng", "Hợp đồng mua sắm", "Hợp đồng thuê đất/xưởng", "Hợp đồng dịch vụ kỹ thuật"],
        "lbl_amount": "Tổng giá trị (VND) *",
        "lbl_date": "Ngày ký *",
        "lbl_status": "Trạng thái *",
        "status_opts": ["Đang thực hiện (Active)", "Đã hoàn thành (Closed)", "Tạm ngưng (Suspended)", "Đang duyệt (Reviewing)"],
        "btn_save": "💾 Tạo hồ sơ hợp đồng",
        "success_save": "✅ Đã tạo thành công hợp đồng `{code}`!",
        "fill_warning": "⚠️ Vui lòng điền Mã hợp đồng, Tên và Đối tác!",
        "upload_header": "📤 Tải lên file hợp đồng cũ cho Quản lý kiểm tra",
        "select_upload_contract": "Chọn dự án hợp đồng tương ứng *",
        "lbl_file": "Chọn file hợp đồng (.pdf, .doc, .docx, .xls)",
        "btn_upload_file": "🚀 Tải lên file hợp đồng",
        "success_upload": "✅ Đã tải lên thành công file `{filename}`!",
        "col_index": "STT",
        "col_code": "Mã HĐ",
        "col_name": "Tên hợp đồng",
        "col_party": "Đối tác",
        "col_type": "Loại",
        "col_amount": "Giá trị (VND)",
        "col_date": "Ngày ký",
        "col_status": "Trạng thái",
        "col_file": "File đính kèm"
    },
    "English": {
        "title": "✍️ GA - Enterprise Contract Management & Review Center",
        "caption": "Manage engineering, equipment procurement, and lease contracts with inline editing and document uploads for management review.",
        "tab_list": "📑 Contract List & Inline Editing",
        "tab_add": "➕ Register New Contract",
        "tab_upload": "📤 Upload Old Contracts for Review",
        "table_header": "📋 Active Enterprise Contracts Overview",
        "no_records": "No contract records found.",
        "edit_header": "✏️ Edit Contract Details",
        "select_contract": "Select Contract to Edit *",
        "btn_update": "💾 Save Changes",
        "success_update": "✅ Contract `{code}` updated successfully!",
        "add_header": "➕ Register New Contract",
        "lbl_code": "Contract No. *",
        "lbl_name": "Contract Name / Project *",
        "lbl_party": "Counterparty (Customer/Supplier) *",
        "party_placeholder": "Example: Ho Team Construction Co., Ltd.",
        "lbl_type": "Contract Type *",
        "type_opts": ["Engineering Contract", "Equipment Procurement", "Land & Lease Agreement", "Technical Service Contract"],
        "lbl_amount": "Total Amount (VND) *",
        "lbl_date": "Signing Date *",
        "lbl_status": "Status *",
        "status_opts": ["Active", "Closed", "Suspended", "Reviewing"],
        "btn_save": "💾 Create Contract Record",
        "success_save": "✅ Contract `{code}` successfully created!",
        "fill_warning": "⚠️ Please fill in Contract No., Name, and Counterparty!",
        "upload_header": "📤 Upload Old Contract Files for Management Review",
        "select_upload_contract": "Select Target Contract *",
        "lbl_file": "Choose Contract File (.pdf, .doc, .docx, .xls)",
        "btn_upload_file": "🚀 Confirm File Upload",
        "success_upload": "✅ File `{filename}` uploaded successfully!",
        "col_index": "No.",
        "col_code": "Contract No.",
        "col_name": "Contract Name",
        "col_party": "Counterparty",
        "col_type": "Type",
        "col_amount": "Amount (VND)",
        "col_date": "Date",
        "col_status": "Status",
        "col_file": "Attachment"
    }
}

def render_contract_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = CONTRACT_I18N.get(active_lang, CONTRACT_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化合約資料庫
    if "enterprise_contracts_db" not in st.session_state:
        st.session_state.enterprise_contracts_db = [
            {
                "code": "HD-2025-HOT",
                "name": "美順工業區電力及給排水系統工程",
                "party": "和鼎隆建築責任有限公司 (Ho Team)",
                "type": "工程承攬合約",
                "amount": 48200946580.0,
                "date": "2025-07-28",
                "status": "進行中 (Active)",
                "file": "HD022026-KS JIAWEI .docx"
            },
            {
                "code": "HD-2026-JIA",
                "name": "嘉威商旅電力系統與水電工程",
                "party": "嘉威商旅責任有限公司 (Jia Wei)",
                "type": "工程承攬合約",
                "amount": 21859200000.0,
                "date": "2026-07-28",
                "status": "進行中 (Active)",
                "file": "HD22驗收.doc"
            },
            {
                "code": "HD-2026-YAN",
                "name": "廠區高低壓配電盤設備採購",
                "party": "彥豪金屬工業股份有限公司",
                "type": "設備採購合約",
                "amount": 28321920000.0,
                "date": "2026-03-15",
                "status": "進行中 (Active)",
                "file": "2026年工程請款對帳單明細.xls"
            }
        ]

    tab_list, tab_add, tab_upload = st.tabs([
        L["tab_list"], L["tab_add"], L["tab_upload"]
    ])

    with tab_list:
        st.markdown(f"### {L['table_header']}")
        if st.session_state.enterprise_contracts_db:
            display_data = []
            for idx, item in enumerate(st.session_state.enterprise_contracts_db, 1):
                display_data.append({
                    L["col_index"]: idx,
                    L["col_code"]: item["code"],
                    L["col_name"]: item["name"],
                    L["col_party"]: item["party"],
                    L["col_type"]: item["type"],
                    L["col_amount"]: f"{item['amount']:,.0f} VND",
                    L["col_date"]: item["date"],
                    L["col_status"]: item["status"],
                    L["col_file"]: item.get("file", "無附件")
                })
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)

            st.markdown("---")
            st.markdown(f"### {L['edit_header']}")
            contract_opts = {f"{item['code']} - {item['name']}": item for item in st.session_state.enterprise_contracts_db}
            selected_key = st.selectbox(L["select_contract"], list(contract_opts.keys()))
            target_contract = contract_opts[selected_key]

            with st.form("form_edit_contract"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("合約名稱", value=target_contract["name"])
                    new_party = st.text_input("簽約對象", value=target_contract["party"])
                    new_type = st.selectbox("合約類型", ["工程承攬合約", "設備採購合約", "土地與廠房租賃", "委任與技術服務合約"], index=0)
                with c2:
                    new_amount = st.number_input("合約金額 (VND)", min_value=0.0, value=float(target_contract["amount"]), step=100000000.0)
                    new_status = st.selectbox("合約狀態", ["進行中 (Active)", "已驗收結案 (Closed)", "暫停中 (Suspended)", "審核中 (Reviewing)"])

                if st.form_submit_button(L["btn_update"], type="primary", use_container_width=True):
                    target_contract["name"] = new_name
                    target_contract["party"] = new_party
                    target_contract["type"] = new_type
                    target_contract["amount"] = new_amount
                    target_contract["status"] = new_status
                    st.success(L["success_update"].format(code=target_contract["code"]))
                    st.rerun()
        else:
            st.info(L["no_records"])

    with tab_add:
        st.markdown(f"### {L['add_header']}")
        with st.form("form_add_contract"):
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input(L["lbl_code"], value="HD-2026-NEW")
                name = st.text_input(L["lbl_name"], value="新專案合約")
                party = st.text_input(L["lbl_party"], placeholder=L["party_placeholder"])
            with c2:
                c_type = st.selectbox(L["lbl_type"], L["type_opts"])
                amount = st.number_input(L["lbl_amount"], min_value=0.0, value=5000000000.0, step=100000000.0)
                c_date = st.date_input(L["lbl_date"], value=datetime.date.today())

            status = st.selectbox(L["lbl_status"], L["status_opts"])

            if st.form_submit_button(L["btn_save"], type="primary", use_container_width=True):
                if code and name and party:
                    st.session_state.enterprise_contracts_db.insert(0, {
                        "code": code,
                        "name": name,
                        "party": party,
                        "type": c_type,
                        "amount": amount,
                        "date": c_date.strftime("%Y-%m-%d"),
                        "status": status,
                        "file": "無附件"
                    })
                    st.success(L["success_save"].format(code=code))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

    with tab_upload:
        st.markdown(f"### {L['upload_header']}")
        contract_opts_up = {f"{item['code']} - {item['name']}": item for item in st.session_state.enterprise_contracts_db}
        selected_up_key = st.selectbox(L["select_upload_contract"], list(contract_opts_up.keys()))
        target_up_contract = contract_opts_up[selected_up_key]

        uploaded_contract_file = st.file_uploader(L["lbl_file"], type=["pdf", "doc", "docx", "xls", "xlsx"])
        if uploaded_contract_file is not None:
            if st.button(L["btn_upload_file"], type="primary"):
                target_up_contract["file"] = uploaded_contract_file.name
                st.success(L["success_upload"].format(filename=uploaded_contract_file.name))

def show(*args, **kwargs):
    render_contract_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_contract_management_page(*args, **kwargs)

def render_contract_management(*args, **kwargs):
    render_contract_management_page(*args, **kwargs)
