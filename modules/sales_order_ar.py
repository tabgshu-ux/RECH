import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 應收帳款與專案進度模組多語系字典 (i18n)
# ----------------------------------------------------
AR_I18N = {
    "繁體中文": {
        "title": "📋 管理部 - 客戶應收帳款 (AR) & 工程分期與對帳中心",
        "caption": "記錄客戶工程合約總額、動態分期付款排程管理、專案說明與進度實時追蹤。",
        "tab_list": "📑 客戶應收款項總表與進度",
        "tab_edit": "✍️ 修改進行進度說明與催收歷程",
        "tab_add": "➕ 登記新應收帳款專案",
        "table_header": "📋 客戶應收帳款專案清冊 (含工程對帳明細)",
        "no_records": "目前無應收帳款紀錄。",
        "read_error": "讀取資料失敗: ",
        "edit_header": "✍️ 修改專案進行進度說明與催收紀錄",
        "select_project": "請選擇要更新進度的請款專案：",
        "current_project": "當前專案",
        "total_amount_label": "總帳款",
        "new_progress_label": "更新「進行進度說明」*",
        "new_reason_label": "更新/追加「催收理由與客戶回應」",
        "modifier_label": "修改人員姓名*",
        "save_update_btn": "💾 儲存並更新專案進度",
        "update_success": "請款單 `{target_id}` 之進行進度與催收理由已更新！",
        "add_header": "➕ 登記新應收帳款專案",
        "inv_id_label": "請款編號 *",
        "entity_name_label": "客戶名稱 *",
        "entity_placeholder": "越南樟榜工業區A廠",
        "project_name_label": "工程名稱 *",
        "project_placeholder": "西寧廠 2000A 配電櫃新建工程",
        "currency_label": "交易幣別 *",
        "currency_opts": ["越南盾 (VND)", "美金 (USD)", "台幣 (TWD)", "人民幣 (CNY)"],
        "usd_label": "總帳款 (USD - 精確至小數點後 3 位) *",
        "total_lbl": "總帳款 *",
        "plan_type_label": "付款期數模式 *",
        "plan_opts": ["不分期", "分三期", "分五期"],
        "proj_desc_label": "專案說明",
        "proj_desc_placeholder": "請填寫本工程施工內容與合約細節...",
        "progress_note_label": "進行進度說明",
        "milestone_header": "💳 分期百分比 (%) 與付款日期細項設定",
        "single_pay_info": "全額一次付清：",
        "payment_date_label": "付款日期",
        "ratio_warning": "⚠️ 目前分期總比率為 `{total_pct}%`（請調整至總和 100%）",
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
        "save_new_btn": "💾 儲存並建立應收請款專案",
        "create_success": "專案 `{inv_id}` 建立成功！",
        "fill_warning": "⚠️ 請完整填寫客戶名稱與工程名稱！",
        "col_index": "STT",
        "col_inv_id": "請款編號",
        "col_entity": "客戶名稱",
        "col_project": "工程名稱",
        "col_currency": "交易幣別",
        "col_total": "總帳款",
        "col_terms": "分期類型",
        "col_ratios": "分期比率",
        "col_progress": "進行進度說明",
        "col_desc": "專案說明",
        "col_reason": "最新催收理由/歷程"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Quản lý - Phải thu Khách hàng (AR) & Đối soát Công trình",
        "caption": "Quản lý tổng số tiền hợp đồng, lịch trình thanh toán theo đợt, cập nhật tiến độ.",
        "tab_list": "📑 Danh sách Phải thu & Tiến độ",
        "tab_edit": "✍️ Cập nhật Tiến độ & Lý do thu nợ",
        "tab_add": "➕ Thêm Dự án Phải thu Mới",
        "table_header": "📋 Sổ chi tiết Phải thu Khách hàng",
        "no_records": "Hiện không có bản ghi khoản phải thu nào.",
        "read_error": "Lỗi đọc dữ liệu: ",
        "edit_header": "✍️ Sửa đổi tiến độ dự án và ghi chú thu nợ",
        "select_project": "Chọn dự án cần cập nhật tiến độ:",
        "current_project": "Dự án hiện tại",
        "total_amount_label": "Tổng tiền",
        "new_progress_label": "Cập nhật Mô tả tiến độ *",
        "new_reason_label": "Cập nhật/Bổ sung Lý do thu nợ & phản hồi từ khách hàng",
        "modifier_label": "Họ tên người sửa*",
        "save_update_btn": "💾 Lưu và cập nhật tiến độ dự án",
        "update_success": "Đã cập nhật tiến độ và lý do thu nợ cho hóa đơn `{target_id}`!",
        "add_header": "➕ Đăng ký dự án khoản phải thu mới",
        "inv_id_label": "Mã hóa đơn / khoản thu *",
        "entity_name_label": "Tên khách hàng *",
        "entity_placeholder": "Nhà máy A KCN Trảng Bàng, Tây Ninh",
        "project_name_label": "Tên công trình *",
        "project_placeholder": "Lắp đặt tủ điện 2000A nhà máy Tây Ninh",
        "currency_label": "Loại tiền tệ *",
        "currency_opts": ["Đồng Việt Nam (VND)", "Đô la Mỹ (USD)", "Đài tệ (TWD)", "Nhân dân tệ (CNY)"],
        "usd_label": "Tổng tiền (USD - Chính xác đến 3 chữ số thập phân) *",
        "total_lbl": "Tổng tiền *",
        "plan_type_label": "Hình thức thanh toán *",
        "plan_opts": ["Thanh toán 1 lần", "Thanh toán 3 đợt", "Thanh toán 5 đợt"],
        "proj_desc_label": "Mô tả dự án",
        "proj_desc_placeholder": "Nhập nội dung thi công và chi tiết hợp đồng...",
        "progress_note_label": "Mô tả tiến độ",
        "milestone_header": "💳 Thiết lập tỷ lệ phần trăm (%) và ngày thanh toán theo đợt",
        "single_pay_info": "Thanh toán 100% một lần:",
        "payment_date_label": "Ngày thanh toán",
        "ratio_warning": "⚠️ Tổng tỷ lệ hiện tại là `{total_pct}%` (Vui lòng điều chỉnh tổng bằng 100%)",
        "ratio_success": "✅ Tổng tỷ lệ phân kỳ đúng 100%",
        "period_1_amt": "Số tiền đợt 1",
        "period_1_date": "Ngày thu đợt 1",
        "period_2_amt": "Số tiền đợt 2",
        "period_2_date": "Ngày thu đợt 2",
        "period_3_amt": "Số tiền đợt 3",
        "period_3_date": "Ngày thu đợt 3",
        "period_4_amt": "Số tiền đợt 4",
        "period_4_date": "Ngày thu đợt 4",
        "period_5_amt": "Số tiền đợt 5",
        "period_5_date": "Ngày thu đợt 5",
        "save_new_btn": "💾 Lưu và đăng ký dự án phải thu",
        "create_success": "Đã tạo thành công dự án `{inv_id}`!",
        "fill_warning": "⚠️ Vui lòng điền đầy đủ Tên khách hàng và Tên công trình!",
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
        "col_reason": "Lịch sử thu nợ"
    },
    "English": {
        "title": "📋 Admin - Accounts Receivable (AR) & Project Installments",
        "caption": "Track total contract amounts, installment schedules, descriptions, and progress updates.",
        "tab_list": "📑 AR Summary & Progress",
        "tab_edit": "✍️ Update Progress & Collection Audit",
        "tab_add": "➕ Register New AR Project",
        "table_header": "📋 Customer Accounts Receivable Registry",
        "no_records": "No accounts receivable records found.",
        "read_error": "Failed to read data: ",
        "edit_header": "✍️ Modify Project Progress & Collection Log",
        "select_project": "Select project to update:",
        "current_project": "Current Project",
        "total_amount_label": "Total Amount",
        "new_progress_label": "Update Progress Description *",
        "new_reason_label": "Update/Append Collection Remarks & Client Feedback",
        "modifier_label": "Modifier Name *",
        "save_update_btn": "💾 Save & Update Project Progress",
        "update_success": "Progress and collection reasons for invoice `{target_id}` updated successfully!",
        "add_header": "➕ Register New Accounts Receivable Project",
        "inv_id_label": "Invoice ID *",
        "entity_name_label": "Client Name *",
        "entity_placeholder": "Tay Ninh Plant Client A",
        "project_name_label": "Project Name *",
        "project_placeholder": "Tay Ninh 2000A Switchboard Installation",
        "currency_label": "Currency *",
        "currency_opts": ["VND", "USD", "TWD", "CNY"],
        "usd_label": "Total Amount (USD - 3 decimal places) *",
        "total_lbl": "Total Amount *",
        "plan_type_label": "Payment Terms *",
        "plan_opts": ["Lump Sum (Single)", "3 Installments", "5 Installments"],
        "proj_desc_label": "Project Description",
        "proj_desc_placeholder": "Enter construction scope and contract details...",
        "progress_note_label": "Progress Description",
        "milestone_header": "💳 Milestone Installment Percentage (%) & Due Dates",
        "single_pay_info": "Full payment in one lump sum:",
        "payment_date_label": "Payment Due Date",
        "ratio_warning": "⚠️ Total ratio is currently `{total_pct}%` (Please adjust to sum up to 100%)",
        "ratio_success": "✅ Installment ratios sum up to 100%",
        "period_1_amt": "Period 1 Amount",
        "period_1_date": "Period 1 Due Date",
        "period_2_amt": "Period 2 Amount",
        "period_2_date": "Period 2 Due Date",
        "period_3_amt": "Period 3 Amount",
        "period_3_date": "Period 3 Due Date",
        "period_4_amt": "Period 4 Amount",
        "period_4_date": "Period 4 Due Date",
        "period_5_amt": "Period 5 Amount",
        "period_5_date": "Period 5 Due Date",
        "save_new_btn": "💾 Save & Register AR Project",
        "create_success": "Project `{inv_id}` successfully created!",
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
        "col_reason": "Collection History"
    }
}

def smart_translate(text_val, target_lang):
    if not text_val or not isinstance(text_val, str) or text_val.strip() in ["None", "-", ""]:
        if target_lang == "Tiếng Việt": return "Chưa cập nhật"
        elif target_lang == "English": return "N/A"
        return "-"
    return text_val

def format_curr(amt, curr):
    if not curr: curr = "越南盾"
    if "VND" in curr or "越南盾" in curr or "Đồng" in curr: return f"₫ {amt:,.0f} VND"
    elif "USD" in curr or "美金" in curr or "Đô la" in curr: return f"$ {amt:,.3f} USD"
    return f"{amt:,.3f} {curr}"

def render_sales_order_ar_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = AR_I18N.get(active_lang, AR_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_edit, tab_add = st.tabs([L["tab_list"], L["tab_edit"], L["tab_add"]])

    # 1. 應收帳款總覽清單與工程對帳單明細
    with tab_list:
        st.subheader(L["table_header"])
        default_ar_records = [
            {"invoice_id": "HD-2026-01", "entity_name": "和鼎隆建築責任有限公司 (Ho Team)", "project_name": "廠房電力系統與給排水統包工程", "currency": "VND", "quoted_amount": 222171208288.0, "payment_terms": "分五期", "installment_ratios": "20% / 20% / 20% / 20% / 20%", "progress_note": "施工完成 71.4%, 待驗收", "project_desc": "合約總價 222,171,208,288 VND | 已收: 160,661,508,865 VND | AR: 61,509,699,423 VND", "uncollected_reason": "正常履約中"},
            {"invoice_id": "HD-2026-02", "entity_name": "第一傳動越南責任有限公司 (Timotion)", "project_name": "高低壓配電站與自動化線路", "currency": "VND", "quoted_amount": 50978160000.0, "payment_terms": "分五期", "installment_ratios": "30% / 20% / 30% / 15% / 5%", "progress_note": "變電站與配電盤送電完成", "project_desc": "合約總價 50,978,160,000 VND | 已收: 14,488,848,000 VND | AR: 36,489,312,000 VND", "uncollected_reason": "待驗收合格後請款"},
            {"invoice_id": "HD-2026-03", "entity_name": "越南佳威實業有限公司 (Jia Wei)", "project_name": "寧平省美順工業區電力及給排水系統", "currency": "VND", "quoted_amount": 21859200000.0, "payment_terms": "分四期", "installment_ratios": "30% / 20% / 30% / 20%", "progress_note": "過路橋架施工完成，電站送電中", "project_desc": "合約總價 21,859,200,000 VND | 已收: 0 VND | AR: 21,859,200,000 VND", "uncollected_reason": "依約定進度請款中"},
            {"invoice_id": "HD-2026-04", "entity_name": "彥豪智能科技（越南）責任有限公司", "project_name": "智能廠房電力與控制系統", "currency": "VND", "quoted_amount": 40955200000.0, "payment_terms": "分三期", "installment_ratios": "20% / 50% / 30%", "progress_note": "簽定訂金完成，依驗收記錄請款", "project_desc": "合約總價 40,955,200,000 VND | 已收: 13,078,029,218 VND | AR: 27,877,170,782 VND", "uncollected_reason": "等待工程驗收單確認"}
        ]

        df_ar = pd.DataFrame()
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
            except Exception:
                pass

        if df_ar.empty:
            df_ar = pd.DataFrame(default_ar_records)

        if not df_ar.empty:
            display_list = []
            for idx, r in df_ar.iterrows():
                entity_display = smart_translate(str(r.get("entity_name", "")), active_lang)
                project_display = smart_translate(str(r.get("project_name", "")), active_lang)
                progress_display = smart_translate(str(r.get("progress_note", "")), active_lang)
                terms_display = smart_translate(str(r.get("payment_terms", "")), active_lang)
                desc_display = smart_translate(str(r.get("project_desc", "")), active_lang)

                display_list.append({
                    L["col_index"]:
