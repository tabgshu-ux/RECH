import streamlit as st
import pandas as pd
import datetime
import os

CONTRACT_I18N = {
    "繁體中文": {
        "title": "✍️ 管理部 - 企業合約管理與主管審查中心",
        "caption": "管理裕豐電機工業各項工程合約、設備採購合約與租賃合約，支援合約清冊檢視、電子檔直接開啟下載、線上修改、刪除與舊合約上傳。",
        "tab_list": "📑 合約清冊與電子檔開啟",
        "tab_add": "➕ 新增合約登記",
        "tab_upload": "📤 上傳舊合約檔案",
        "table_header": "📋 裕豐電機工業現行合約總覽",
        "no_records": "目前無合約紀錄。",
        
        # 電子檔檢視與下載部分
        "file_viewer_header": "📂 開啟與下載合約電子檔 (Management Viewer)",
        "select_file_target": "選擇要檢視/下載電子檔的合約 *",
        "file_found": "✅ 找到對應的合約檔案：`{filename}`",
        "file_not_found": "⚠️ 系統目錄中尚未找到實體檔案 `{filename}`（可至上傳分頁補上傳），以下提供直接下載模擬：",
        "btn_download_file": "📥 點擊下載 / 開啟合約電子檔",

        "edit_header": "✏️ 線上修改或刪除合約資料",
        "select_contract": "選擇要修改/刪除的合約 *",
        "lbl_edit_name": "合約名稱 / 專案主題 *",
        "lbl_edit_party": "簽約對象 *",
        "lbl_edit_type": "合約類型 *",
        "lbl_edit_amount": "合約金額 (VND) *",
        "lbl_edit_status": "合約狀態 *",
        "btn_update": "💾 儲存修改內容",
        "btn_delete": "🗑️ 刪除此合約",
        "success_update": "✅ 合約 `{code}` 資料已成功更新！",
        "success_delete": "🗑️ 合約 `{code}` 已成功刪除！",
        
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
        
        "upload_header": "📤 上傳舊合約檔案",
        "lbl_upload_code": "合約編號 *",
        "lbl_upload_name": "合約名稱 / 專案主題 *",
        "lbl_upload_party": "簽約對方 / 客戶名稱 *",
        "lbl_file": "選擇合約檔案 (.pdf, .doc, .docx, .xls, .xlsx) *",
        "btn_upload_file": "🚀 上傳檔案",
        "success_upload": "✅ 檔案 `{filename}` 已成功上傳！",
        "upload_warning": "⚠️ 請填寫完整資料並選擇檔案！",

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
        "title": "✍️ Khối Hành chính - Quản lý Hợp đồng & Phê duyệt",
        "caption": "Quản lý hợp đồng; hỗ trợ xem file, chỉnh sửa, xóa và tải lên.",
        "tab_list": "📑 Danh sách & Mở file Hợp đồng",
        "tab_add": "➕ Đăng ký Hợp đồng Mới",
        "tab_upload": "📤 Tải lên Hợp đồng Cũ",
        "table_header": "📋 Tổng quan Hợp đồng hiện hành",
        "no_records": "Hiện không có bản ghi hợp đồng nào.",
        "file_viewer_header": "📂 Mở và Tải xuống File Hợp đồng",
        "select_file_target": "Chọn hợp đồng cần xem file *",
        "file_found": "✅ Đã tìm thấy file: `{filename}`",
        "file_not_found": "⚠️ Chưa có file thực tế `{filename}`, hỗ trợ tải file mẫu:",
        "btn_download_file": "📥 Tải xuống / Mở file hợp đồng",
        "edit_header": "✏️ Chỉnh sửa hoặc xóa thông tin hợp đồng",
        "select_contract": "Chọn hợp đồng cần sửa/xóa *",
        "lbl_edit_name": "Tên hợp đồng *",
        "lbl_edit_party": "Đối tác *",
        "lbl_edit_type": "Loại *",
        "lbl_edit_amount": "Giá trị (VND) *",
        "lbl_edit_status": "Trạng thái *",
        "btn_update": "💾 Lưu thay đổi",
        "btn_delete": "🗑️ Xóa",
        "success_update": "✅ Đã cập nhật thành công!",
        "success_delete": "🗑️ Đã xóa thành công!",
        "add_header": "➕ Đăng ký hợp đồng mới",
        "lbl_code": "Mã hợp đồng *",
        "lbl_name": "Tên hợp đồng *",
        "lbl_party": "Đối tác *",
        "party_placeholder": "Ví dụ: Ho Team",
        "lbl_type": "Loại hợp đồng *",
        "type_opts": ["Hợp đồng xây dựng", "Hợp đồng mua sắm", "Hợp đồng thuê đất", "Hợp đồng dịch vụ"],
        "lbl_amount": "Tổng giá trị (VND) *",
        "lbl_date": "Ngày ký *",
        "lbl_status": "Trạng thái *",
        "status_opts": ["Đang thực hiện (Active)", "Đã hoàn thành (Closed)"],
        "btn_save": "💾 Tạo hồ sơ",
        "success_save": "✅ Đã tạo thành công!",
        "fill_warning": "⚠️ Vui lòng điền đủ thông tin!",
        "upload_header": "📤 Tải lên file hợp đồng cũ",
        "lbl_upload_code": "Mã hợp đồng *",
        "lbl_upload_name": "Tên hợp đồng *",
        "lbl_upload_party": "Tên đối tác *",
        "lbl_file": "Chọn file *",
        "btn_upload_file": "🚀 Tải lên",
        "success_upload": "✅ Đã tải lên thành công!",
        "upload_warning": "⚠️ Vui lòng điền đủ thông tin!",
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
        "caption": "Manage contracts with file viewing/downloading, editing, deletion, and old contract uploads.",
        "tab_list": "📑 Contract List & File Viewer",
        "tab_add": "➕ Register New Contract",
        "tab_upload": "📤 Upload Old Contracts",
        "table_header": "📋 Active Enterprise Contracts Overview",
        "no_records": "No contract records found.",
        "file_viewer_header": "📂 Open & Download Contract Electronic File",
        "select_file_target": "Select Contract to View/Download File *",
        "file_found": "✅ File found: `{filename}`",
        "file_not_found": "⚠️ Physical file `{filename}` not found in root directory yet, download simulation available:",
        "btn_download_file": "📥 Download / Open Contract File",
        "edit_header": "✏️ Edit or Delete Contract Details",
        "select_contract": "Select Contract to Edit/Delete *",
        "lbl_edit_name": "Contract Name *",
        "lbl_edit_party": "Counterparty *",
        "lbl_edit_type": "Contract Type *",
        "lbl_edit_amount": "Amount (VND) *",
        "lbl_edit_status": "Status *",
        "btn_update": "💾 Save Changes",
        "btn_delete": "🗑️ Delete Contract",
        "success_update": "✅ Contract updated successfully!",
        "success_delete": "🗑️ Contract deleted successfully!",
        "add_header": "➕ Register New Contract",
        "lbl_code": "Contract No. *",
        "lbl_name": "Contract Name *",
        "lbl_party": "Counterparty *",
        "party_placeholder": "Example: Ho Team",
        "lbl_type": "Contract Type *",
        "type_opts": ["Engineering Contract", "Equipment Procurement", "Land Lease", "Technical Service"],
        "lbl_amount": "Amount (VND) *",
        "lbl_date": "Date *",
        "lbl_status": "Status *",
        "status_opts": ["Active", "Closed"],
        "btn_save": "💾 Create Record",
        "success_save": "✅ Created successfully!",
        "fill_warning": "⚠️ Please fill in all fields!",
        "upload_header": "📤 Upload Old Contract File",
        "lbl_upload_code": "Contract No. *",
        "lbl_upload_name": "Contract Name *",
        "lbl_upload_party": "Counterparty *",
        "lbl_file": "Choose File *",
        "btn_upload_file": "🚀 Upload",
        "success_upload": "✅ File uploaded successfully!",
        "upload_warning": "⚠️ Please fill in all fields!",
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

            # 新增：電子檔檢視與開啟下載專區
            st.markdown("---")
            st.markdown(f"### {L['file_viewer_header']}")
            file_opts = {f"{item['code']} - {item['name']} ({item.get('file', '無附件')})": item for item in st.session_state.enterprise_contracts_db}
            selected_file_key = st.selectbox(L["select_file_target"], list(file_opts.keys()))
            target_file_item = file_opts[selected_file_key]
            filename = target_file_item.get("file", "")

            if filename and filename != "無附件":
                file_path = filename
                if os.path.exists(file_path):
                    st.success(L["file_found"].format(filename=filename))
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    st.download_button(
                        label=L["btn_download_file"],
                        data=file_bytes,
                        file_name=filename,
                        mime="application/octet-stream",
                        type="primary",
                        use_container_width=True
                    )
                else:
                    st.warning(L["file_not_found"].format(filename=filename))
                    st.download_button(
                        label=L["btn_download_file"],
                        data=b"Mock contract electronic document content for " + filename.encode(),
                        file_name=filename,
                        mime="application/octet-stream",
                        use_container_width=True
                    )
            else:
                st.info("此合約目前尚無上傳電子檔附件。")

            st.markdown("---")
            st.markdown(f"### {L['edit_header']}")
            contract_opts = {f"{item['code']} - {item['name']}": item for item in st.session_state.enterprise_contracts_db}
            selected_key = st.selectbox(L["select_contract"], list(contract_opts.keys()))
            target_contract = contract_opts[selected_key]

            with st.form("form_edit_contract"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input(L["lbl_edit_name"], value=target_contract["name"])
                    new_party = st.text_input(L["lbl_edit_party"], value=target_contract["party"])
                    new_type = st.selectbox(L["lbl_edit_type"], ["工程承攬合約", "設備採購合約", "土地與廠房租賃", "委任與技術服務合約"], index=0)
                with c2:
                    new_amount = st.number_input(L["lbl_edit_amount"], min_value=0.0, value=float(target_contract["amount"]), step=100000000.0)
                    new_status = st.selectbox(L["lbl_edit_status"], ["進行中 (Active)", "已驗收結案 (Closed)", "暫停中 (Suspended)", "審核中 (Reviewing)"])

                col_btn1, col_btn2 = st.columns(2)
                submitted_update = col_btn1.form_submit_button(L["btn_update"], type="primary", use_container_width=True)
                submitted_delete = col_btn2.form_submit_button(L["btn_delete"], type="secondary", use_container_width=True)

                if submitted_update:
                    target_contract["name"] = new_name
                    target_contract["party"] = new_party
                    target_contract["type"] = new_type
                    target_contract["amount"] = new_amount
                    target_contract["status"] = new_status
                    st.success(L["success_update"].format(code=target_contract["code"]))
                    st.rerun()
                elif submitted_delete:
                    st.session_state.enterprise_contracts_db = [
                        item for item in st.session_state.enterprise_contracts_db if item["code"] != target_contract["code"]
                    ]
                    st.success(L["success_delete"].format(code=target_contract["code"]))
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
                amount = st.number_input(L["lbl_amount"], min_value=0.0, value=5000000000.0, step=500000000.0)
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
        with st.form("form_upload_old_contract"):
            up_code = st.text_input(L["lbl_upload_code"], value="OLD-2024-DOC")
            up_name = st.text_input(L["lbl_upload_name"], value="舊合約檔案")
            up_party = st.text_input(L["lbl_upload_party"], placeholder="例如: 某某供應商 / 業主")
            
            uploaded_file = st.file_uploader(L["lbl_file"], type=["pdf", "doc", "docx", "xls", "xlsx"])
            
            if st.form_submit_button(L["btn_upload_file"], type="primary", use_container_width=True):
                if up_code and up_name and up_party and uploaded_file is not None:
                    st.session_state.enterprise_contracts_db.insert(0, {
                        "code": up_code,
                        "name": up_name,
                        "party": up_party,
                        "type": "歷史舊合約",
                        "amount": 0.0,
                        "date": datetime.date.today().strftime("%Y-%m-%d"),
                        "status": "已歸檔",
                        "file": uploaded_file.name
                    })
                    st.success(L["success_upload"].format(filename=uploaded_file.name))
                    st.rerun()
                else:
                    st.warning(L["upload_warning"])

def show(*args, **kwargs):
    render_contract_management_page(*args, **kwargs)

def main(*args, **kwargs):
    render_contract_management_page(*args, **kwargs)

def render_contract_management(*args, **kwargs):
    render_contract_management_page(*args, **kwargs)
