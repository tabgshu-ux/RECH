import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 📱 手機優先響應式 CSS 注入 (Mobile-First UI)
# ----------------------------------------------------
MOBILE_AR_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.3rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.85rem !important; }
    .stDataFrame { overflow-x: auto; }
    .stButton button { width: 100% !important; }
}
</style>
"""
st.markdown(MOBILE_AR_CSS, unsafe_allow_html=True)

# ----------------------------------------------------
# 🌐 應收帳款與專案進度模組多語系字典 (i18n)
# ----------------------------------------------------
AR_I18N = {
    "繁體中文": {
        "title": "📋 管理部 - 客戶應收帳款 (AR) & 專案分期進度管理",
        "caption": "記錄客戶工程合約總額、動態分期付款排程管理、專案說明與進度實時追蹤、催收歷程與拒付呆帳風險管理。",
        "tab_list": "📑 應收款項總表與進度",
        "tab_edit": "✍️ 進度說明與催收歷程",
        "tab_add": "➕ 登記新應收專案",
        "table_header": "📋 客戶應收帳款專案清冊與催收歷程",
        "no_records": "目前無應收帳款紀錄。",
        "read_error": "讀取資料失敗: ",
        "edit_header": "✍️ 專案進行進度與期數催收歷程",
        "select_project": "請選擇請款專案：",
        "current_project": "當前專案",
        "total_amount_label": "總帳款",
        "target_milestone_label": "指定付款期數 *",
        "milestone_opts": ["全部期數 / 總合約", "第一期款 (訂金)", "第二期款", "第三期款", "第四期款", "尾款 / 驗收保留款", "保固金"],
        "progress_note_label": "進行進度說明 *",
        "reason_label": "催收歷程、客戶拒付原因或呆帳風險評估 *",
        "modifier_label": "經辦人員 (系統綁定登入帳號)",
        "save_update_btn": "💾 儲存專案進度與催收歷程",
        "update_success": "請款單之進度與催收紀錄已成功儲存！",
        "add_header": "➕ 登記新應收帳款專案",
        "inv_id_label": "請款編號 *",
        "entity_name_label": "客戶名稱 *",
        "entity_placeholder": "越南樟榜工業區A廠",
        "project_name_label": "工程名稱 *",
        "project_placeholder": "西寧廠 2000A 配電櫃新建工程",
        "currency_label": "交易幣別 *",
        "currency_opts": ["越南盾", "美金", "台幣", "人民幣"],
        "usd_label": "總帳款 (USD - 精確至小數點後 3 位) *",
        "total_lbl": "總帳款 *",
        "plan_type_label": "付款期數模式 *",
        "plan_opts": ["不分期", "分三期", "分五期"],
        "proj_desc_label": "專案說明",
        "proj_desc_placeholder": "請填寫本工程施工內容與合約細節...",
        "milestone_header": "💳 分期百分比 (%) 與付款日期細項設定",
        "single_pay_info": "全額一次付清：",
        "payment_date_label": "付款日期",
        "ratio_warning": "⚠️ 目前分期總比率為總和 100%",
        "ratio_success": "✅ 分期比率總和剛好 100%",
        "period_1_amt": "第一期金額",
        "period_1_date": "第一期收款日期",
        "period_2_amt": "第二期金額",
        "period_2_date": "第二期收款日期",
        "period_3_amt": "第三期金額",
        "period_3_date": "第三期收款日期",
        "period_4_amt": "第四期金額",
        "period_4_date": "第四期收款日期",
        "period_5_amt": "第五期金額",
        "period_5_date": "第五期收款日期",
        "save_new_btn": "💾 建立應收請款專案",
        "create_success": "專案建立成功！",
        "fill_warning": "⚠️ 請完整填寫客戶名稱與工程名稱！",
        "col_index": "編號",
        "col_inv_id": "請款編號",
        "col_entity": "客戶名稱",
        "col_project": "工程名稱",
        "col_currency": "交易幣別",
        "col_total": "總帳款",
        "col_terms": "分期類型",
        "col_ratios": "分期比率",
        "col_progress": "進行進度說明",
        "col_desc": "專案說明",
        "col_reason": "催收歷程與拒付/呆帳備忘"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Quản lý - Phải thu Khách hàng (AR) & Tiến độ Dự án",
        "caption": "Quản lý tổng số tiền hợp đồng, lịch trình thanh toán, lịch sử thu nợ, lý do từ chối thanh toán và rủi ro nợ xấu.",
        "tab_list": "📑 Danh sách Phải thu",
        "tab_edit": "✍️ Tiến độ & Thu nợ",
        "tab_add": "➕ Thêm Dự án Mới",
        "table_header": "📋 Sổ chi tiết Phải thu Khách hàng",
        "no_records": "Hiện không có bản ghi khoản phải thu nào.",
        "read_error": "Lỗi đọc dữ liệu: ",
        "edit_header": "✍️ Tiến độ dự án & Lịch sử thu nợ theo đợt",
        "select_project": "Chọn dự án cần cập nhật:",
        "current_project": "Dự án hiện tại",
        "total_amount_label": "Tổng tiền",
        "target_milestone_label": "Đợt thanh toán *",
        "milestone_opts": ["Tất cả các đợt", "Đợt 1 (Đặt cọc)", "Đợt 2", "Đợt 3", "Đợt 4", "Đợt cuối / Giữ bảo hành", "Tiền bảo hành"],
        "progress_note_label": "Mô tả tiến độ *",
        "reason_label": "Lịch sử thu nợ, lý do từ chối hoặc rủi ro nợ xấu *",
        "modifier_label": "Người thực hiện (Hệ thống khóa)",
        "save_update_btn": "💾 Lưu tiến độ & Lịch sử thu nợ",
        "update_success": "Đã cập nhật tiến độ thành công!",
        "add_header": "➕ Đăng ký dự án khoản phải thu mới",
        "inv_id_label": "Mã hóa đơn *",
        "entity_name_label": "Tên khách hàng *",
        "entity_placeholder": "Nhà máy A KCN Trảng Bàng, Tây Ninh",
        "project_name_label": "Tên công trình *",
        "project_placeholder": "Lắp đặt tủ điện 2000A nhà máy Tây Ninh",
        "currency_label": "Loại tiền tệ *",
        "currency_opts": ["Đồng Việt Nam (VND)", "Đô la Mỹ (USD)", "Đài tệ (TWD)", "Nhân dân tệ (CNY)"],
        "usd_label": "Tổng tiền (USD) *",
        "total_lbl": "Tổng tiền *",
        "plan_type_label": "Hình thức thanh toán *",
        "plan_opts": ["Thanh toán 1 lần", "Thanh toán 3 đợt", "Thanh toán 5 đợt"],
        "proj_desc_label": "Mô tả dự án",
        "proj_desc_placeholder": "Nhập nội dung thi công...",
        "milestone_header": "💳 Thiết lập tỷ lệ phần trăm (%) theo đợt",
        "single_pay_info": "Thanh toán 100%:",
        "payment_date_label": "Ngày thanh toán",
        "ratio_warning": "⚠️ Tổng tỷ lệ hiện tại chưa đủ 100%",
        "ratio_success": "✅ Tổng tỷ lệ đúng 100%",
        "period_1_amt": "Số tiền đợt 1",
        "period_1_date": "Ngày đợt 1",
        "period_2_amt": "Số tiền đợt 2",
        "period_2_date": "Ngày đợt 2",
        "period_3_amt": "Số tiền đợt 3",
        "period_3_date": "Ngày đợt 3",
        "period_4_amt": "Số tiền đợt 4",
        "period_4_date": "Ngày đợt 4",
        "period_5_amt": "Số tiền đợt 5",
        "period_5_date": "Ngày đợt 5",
        "save_new_btn": "💾 Lưu dự án phải thu",
        "create_success": "Đã tạo thành công dự án mới!",
        "fill_warning": "⚠️ Vui lòng điền Tên khách hàng và Tên công trình!",
        "col_index": "STT",
        "col_inv_id": "Mã hóa đơn",
        "col_entity": "Tên khách hàng",
        "col_project": "Tên công trình",
        "col_currency": "Loại tiền",
        "col_total": "Tổng tiền",
        "col_terms": "Hình thức",
        "col_ratios": "Tỷ lệ đợt",
        "col_progress": "Mô tả tiến độ",
        "col_desc": "Mô tả dự án",
        "col_reason": "Lịch sử thu nợ & Rủi ro"
    },
    "English": {
        "title": "📋 Admin - Accounts Receivable (AR) & Project Installments",
        "caption": "Track total contract amounts, installment schedules, collection logs, and default risks.",
        "tab_list": "📑 AR Summary",
        "tab_edit": "✍️ Progress & Collection",
        "tab_add": "➕ Register AR",
        "table_header": "📋 Customer Accounts Receivable Registry",
        "no_records": "No records found.",
        "read_error": "Failed to read data: ",
        "edit_header": "✍️ Project Progress & Milestone Collection Log",
        "select_project": "Select project:",
        "current_project": "Current Project",
        "total_amount_label": "Total Amount",
        "target_milestone_label": "Payment Milestone *",
        "milestone_opts": ["All Milestones / Total", "Period 1 (Deposit)", "Period 2", "Period 3", "Period 4", "Final / Retention", "Warranty Deposit"],
        "progress_note_label": "Progress Description *",
        "reason_label": "Collection Log, Rejection Reasons or Default Risk *",
        "modifier_label": "Modifier (System Bound)",
        "save_update_btn": "💾 Save Progress & Collection Log",
        "update_success": "Progress saved successfully!",
        "add_header": "➕ Register New AR Project",
        "inv_id_label": "Invoice ID *",
        "entity_name_label": "Client Name *",
        "entity_placeholder": "Tay Ninh Plant Client A",
        "project_name_label": "Project Name *",
        "project_placeholder": "Tay Ninh 2000A Switchboard Installation",
        "currency_label": "Currency *",
        "currency_opts": ["VND", "USD", "TWD", "CNY"],
        "usd_label": "Total Amount (USD) *",
        "total_lbl": "Total Amount *",
        "plan_type_label": "Payment Terms *",
        "plan_opts": ["Lump Sum (Single)", "3 Installments", "5 Installments"],
        "proj_desc_label": "Project Description",
        "proj_desc_placeholder": "Enter scope...",
        "milestone_header": "💳 Milestone Installment Ratios (%)",
        "single_pay_info": "Full payment:",
        "payment_date_label": "Due Date",
        "ratio_warning": "⚠️ Total ratio must be 100%",
        "ratio_success": "✅ Ratios sum up to 100%",
        "period_1_amt": "Period 1",
        "period_1_date": "Date 1",
        "period_2_amt": "Period 2",
        "period_2_date": "Date 2",
        "period_3_amt": "Period 3",
        "period_3_date": "Date 3",
        "period_4_amt": "Period 4",
        "period_4_date": "Date 4",
        "period_5_amt": "Period 5",
        "period_5_date": "Date 5",
        "save_new_btn": "💾 Save AR Project",
        "create_success": "Project successfully created!",
        "fill_warning": "⚠️ Please fill in Client Name and Project Name!",
        "col_index": "No.",
        "col_inv_id": "Invoice ID",
        "col_entity": "Client Name",
        "col_project": "Project Name",
        "col_currency": "Currency",
        "col_total": "Total",
        "col_terms": "Terms",
        "col_ratios": "Installment Ratios",
        "col_progress": "Progress Note",
        "col_desc": "Project Desc",
        "col_reason": "Collection History & Risk"
    }
}

def smart_translate(text_val, target_lang):
    if not text_val or not isinstance(text_val, str) or text_val.strip() in ["None", "-", ""]:
        if target_lang == "Tiếng Việt": return "Chưa cập nhật"
        elif target_lang == "English": return "N/A"
        return "-"

    val_lower = text_val.lower()

    if "樟榜" in text_val or "trảng bàng" in val_lower or "tay ninh" in val_lower or "工業區" in text_val:
        if target_lang == "Tiếng Việt": return "Nhà máy A KCN Trảng Bàng, Tây Ninh"
        elif target_lang == "繁體中文": return "越南樟榜工業區A廠"
        elif target_lang == "English": return "Tay Ninh Plant Client A"

    if "西寧" in text_val or "2000a" in val_lower or "配電櫃" in text_val or "tủ điện" in val_lower or "新建工程" in text_val:
        if target_lang == "Tiếng Việt": return "Lắp đặt tủ điện 2000A nhà máy Tây Ninh"
        elif target_lang == "繁體中文": return "西寧廠 2000A 配電櫃新建工程"
        elif target_lang == "English": return "Tay Ninh 2000A Switchboard Installation"

    if "備料" in text_
