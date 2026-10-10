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

    if "備料" in text_val or "準備" in text_val or "chuẩn bị" in val_lower or "thi công" in val_lower:
        if target_lang == "Tiếng Việt":
            return "Đang chuẩn bị vật tư / Chuẩn bị thi công"
        elif target_lang == "繁體中文":
            return "工程備料中 / 準備施工"
        elif target_lang == "English":
            return "Material preparation / Preparing construction"

    if "不分期" in text_val or "1" in text_val and "đợt" in val_lower or "single" in val_lower or "lump" in val_lower:
        if target_lang == "Tiếng Việt": return "Thanh toán 1 lần"
        elif target_lang == "繁體中文": return "不分期"
        return "Single"
    if "分三期" in text_val or "3" in text_val:
        if target_lang == "Tiếng Việt": return "Thanh toán 3 đợt"
        elif target_lang == "繁體中文": return "分三期"
        return "3 Installments"
    if "分五期" in text_val or "5" in text_val:
        if target_lang == "Tiếng Việt": return "Thanh toán 5 đợt"
        elif target_lang == "繁體中文": return "分五期"
        return "5 Installments"

    return text_val

def format_curr(amt, curr):
    if not curr: curr = "越南盾"
    if "VND" in curr or "越南盾" in curr or "Đồng" in curr: return f"₫ {amt:,.0f} VND"
    elif "USD" in curr or "美金" in curr or "Đô la" in curr: return f"$ {amt:,.3f} USD"
    elif "TWD" in curr or "台幣" in curr or "Đài tệ" in curr: return f"NT$ {amt:,.0f} TWD"
    elif "CNY" in curr or "人民幣" in curr or "Nhân dân tệ" in curr: return f"¥ {amt:,.2f} CNY"
    return f"{amt:,.3f} {curr}"

def render_sales_order_ar_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = AR_I18N.get(active_lang, AR_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_edit, tab_add = st.tabs([L["tab_list"], L["tab_edit"], L["tab_add"]])

    with tab_list:
        st.subheader(L["table_header"])
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    display_list = []
                    for idx, r in df_ar.iterrows():
                        display_list.append({
                            L["col_index"]: idx + 1,
                            L["col_inv_id"]: r.get("invoice_id"),
                            L["col_entity"]: smart_translate(r.get("entity_name"), active_lang),
                            L["col_project"]: smart_translate(r.get("project_name"), active_lang),
                            L["col_currency"]: r.get("currency"),
                            L["col_total"]: format_curr(r.get("quoted_amount", 0.0), r.get("currency")),
                            L["col_terms"]: smart_translate(r.get("payment_terms"), active_lang),
                            L["col_ratios"]: r.get("installment_ratios", "100%"),
                            L["col_progress"]: smart_translate(r.get("progress_note"), active_lang),
                            L["col_desc"]: smart_translate(r.get("project_desc"), active_lang),
                            L["col_reason"]: r.get("uncollected_reason", "-")
                        })
                    st.dataframe(pd.DataFrame(display_list), use_container_width=True)
                else:
                    st.info(L["no_records"])
            except Exception as e:
                st.error(f"{L['read_error']}{e}")

    with tab_edit:
        st.subheader(L["edit_header"])
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    ar_opts = {f"{r['invoice_id']} - {smart_translate(r['entity_name'], active_lang)} ({smart_translate(r['project_name'], active_lang)})": r['invoice_id'] for _, r in df_ar.iterrows()}
                    sel_label = st.selectbox(L["select_project"], list(ar_opts.keys()))
                    target_id = ar_opts[sel_label]
                    target_row = df_ar[df_ar['invoice_id'] == target_id].iloc[0]

                    proj_name_disp = smart_translate(target_row['project_name'], active_lang)
                    st.markdown(f"**{L['current_project']}**：`{proj_name_disp}` | **{L['total_amount_label']}**：{format_curr(target_row['quoted_amount'], target_row['currency'])}")
                    
                    with st.form("form_update_ar_progress"):
                        target_milestone = st.selectbox(L["target_milestone_label"], L["milestone_opts"])
                        
                        default_prog = smart_translate(target_row.get("progress_note", ""), active_lang)
                        new_progress = st.text_area(L["progress_note_label"], value=default_prog)
                        new_reason = st.text_area(L["reason_label"], value=target_row.get("uncollected_reason", ""), placeholder="例如：客戶資金周轉困難要求展延，驗收爭議拒付，或回報該客戶已倒閉/破產清算...")
                        
                        logged_user_name = st.session_state.get("user_name", "admin")
                        logged_user_role = str(st.session_state.get("user_role", "Staff")).upper()
                        modifier_display = f"{logged_user_name} ({logged_user_role})"
                        
                        st.text_input(L["modifier_label"], value=modifier_display, disabled=True)

                        if st.form_submit_button(L["save_update_btn"], type="primary", use_container_width=True):
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            full_reason = f"【{timestamp} | {target_milestone} | 經辦:{modifier_display}】{new_reason}"
                            
                            with engine.connect() as conn:
                                conn.execute(
                                    text("""
                                        UPDATE invoices 
                                        SET progress_note = :prog,
                                            uncollected_reason = :reason,
                                            quoter_name = :quoter
                                        WHERE invoice_id = :id
                                    """),
                                    {"prog": new_progress, "reason": full_reason, "quoter": modifier_display, "id": target_id}
                                )
                                conn.commit()
                            st.success(L["update_success"])
                            st.rerun()
            except Exception as e:
                st.error(f"{L['read_error']}{e}")

    with tab_add:
        st.subheader(L["add_header"])
        
        c1, c2 = st.columns(2)
        with c1:
            inv_id = st.text_input(L["inv_id_label"], value=f"AR-2026-{datetime.datetime.now().strftime('%m%d%H%M')}")
            entity_name = st.text_input(L["entity_name_label"], placeholder=L["entity_placeholder"])
            project_name = st.text_input(L["project_name_label"], placeholder=L["project_placeholder"])
            currency = st.selectbox(L["currency_label"], L["currency_opts"])
            
            if "USD" in currency or "美金" in currency or "Đô la" in currency:
                total_amount = st.number_input(L["usd_label"], min_value=0.0, value=10000.000, format="%.3f", step=0.001)
            else:
                total_amount = st.number_input(L["total_lbl"], min_value=0.0, value=100000.0, step=1000.0)

        with c2:
            plan_type = st.selectbox(L["plan_type_label"], L["plan_opts"])
            project_desc = st.text_area(L["proj_desc_label"], placeholder=L["proj_desc_placeholder"])

        st.markdown("---")
        st.markdown(f"##### {L['milestone_header']}")

        ratios_str = "100%"
        p1_amt, p2_amt, p3_amt, p4_amt, p5_amt = total_amount, 0.0, 0.0, 0.0, 0.0
        d1, d2, d3, d4, d5 = datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today()

        is_single = ("不分期" in plan_type) or ("1" in plan_type and "đợt" in plan_type) or ("Single" in plan_type)
        is_three = ("分三期" in plan_type) or ("3" in plan_type)
        is_five = ("分五期" in plan_type) or ("5" in plan_type)

        if is_single:
            d1 = st.date_input(L["payment_date_label"], value=datetime.date.today() + datetime.timedelta(days=30), key="ar_d_single")
            st.info(f"{L['single_pay_info']} {format_curr(total_amount, currency)}")

        elif is_three:
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                r1 = st.number_input("第 1 期比率 (%)" if active_lang=="繁體中文" else "Tỷ lệ đợt 1 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r1")
            with col_r2:
                r2 = st.number_input("第 2 期比率 (%)" if active_lang=="繁體中文" else "Tỷ lệ đợt 2 (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0, key="ar_3r2")
            with col_r3:
                r3 = st.number_input("第 3 期比率 (%)" if active_lang=="繁體中文" else "Tỷ lệ đợt 3 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r3")
            
            total_pct = r1 + r2 + r3
            if abs(total_pct - 100.0) > 0.01:
                st.warning(L["ratio_warning"])
            else:
                st.success(L["ratio_success"])

            ratios_str = f"{r1}% / {r2}% / {r3}%"
            p1_amt = total_amount * (r1 / 100.0)
            p2_amt = total_amount * (r2 / 100.0)
            p3_amt = total_amount * (r3 / 100.0)

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"• **{L['period_1_amt']}**：`{format_curr(p1_amt, currency)}`")
                d1 = st.date_input(L["period_1_date"], value=datetime.date.today() + datetime.timedelta(days=7), key="ar_3d1")
                st.write(f"• **{L['period_2_amt']}**：`{format_curr(p2_amt, currency)}`")
                d2 = st.date_input(L["period_2_date"], value=datetime.date.today() + datetime.timedelta(days=30), key="ar_3d2")
            with col_b:
                st.write(f"• **{L['period_3_amt']}**：`{format_curr(p3_amt, currency)}`")
                d3 = st.date_input(L["period_3_date"], value=datetime.date.today() + datetime.timedelta(days=60), key="ar_3d3")

        elif is_five:
            col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
            with col_r1:
                r1 = st.number_input("第 1 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r1")
            with col_r2:
                r2 = st.number_input("第 2 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r2")
            with col_r3:
                r3 = st.number_input("第 3 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r3")
            with col_r4:
                r4 = st.number_input("第 4 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r4")
            with col_r5:
                r5 = st.number_input("第 5 期 %", min_value=0.0, max_value=100.0, value=20.0, step=1.0, key="ar_5r5")

            total_pct = r1 + r2 + r3 + r4 + r5
            if abs(total_pct - 100.0) > 0.01:
                st.warning(L["ratio_warning"])
            else:
                st.success(L["ratio_success"])

            ratios_str = f"{r1}% / {r2}% / {r3}% / {r4}% / {r5}%"
            p1_amt = total_amount * (r1 / 100.0)
            p2_amt = total_amount * (r2 / 100.0)
            p3_amt = total_amount * (r3 / 100.0)
            p4_amt = total_amount * (r4 / 100.0)
            p5_amt = total_amount * (r5 / 100.0)

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"• **{L['period_1_amt']}**：`{format_curr(p1_amt, currency)}`")
                d1 = st.date_input(L["period_1_date"], value=datetime.date.today() + datetime.timedelta(days=7), key="ar_5d1")
                st.write(f"• **{L['period_2_amt']}**：`{format_curr(p2_amt, currency)}`")
                d2 = st.date_input(L["period_2_date"], value=datetime.date.today() + datetime.timedelta(days=30), key="ar_5d2")
                st.write(f"• **{L['period_3_amt']}**：`{format_curr(p3_amt, currency)}`")
                d3 = st.date_input(L["period_3_date"], value=datetime.date.today() + datetime.timedelta(days=60), key="ar_5d3")
            with col_b:
                st.write(f"• **{L['period_4_amt']}**：`{format_curr(p4_amt, currency)}`")
                d4 = st.date_input(L["period_4_date"], value=datetime.date.today() + datetime.timedelta(days=90), key="ar_5d4")
                st.write(f"• **{L['period_5_amt']}**：`{format_curr(p5_amt, currency)}`")
                d5 = st.date_input(L["period_5_date"], value=datetime.date.today() + datetime.timedelta(days=120), key="ar_5d5")

        st.markdown("")
        if st.button(L["save_new_btn"], type="primary", use_container_width=True):
            if entity_name and project_name:
                if engine:
                    with engine.connect() as conn:
                        conn.execute(
                            text("""
                                INSERT INTO invoices (
                                    invoice_id, entity_name, project_name, currency, amount, quoted_amount, 
                                    payment_terms, installment_ratios, project_desc, progress_note, 
                                    due_date, invoice_type, is_paid
                                ) VALUES (
                                    :id, :entity, :prj, :curr, :amt, :q_amt, 
                                    :terms, :ratios, :desc, :prog, 
                                    :due, 'AR', false
                                )
                            """),
                            {
                                "id": inv_id, "entity": entity_name, "prj": project_name, "curr": currency,
                                "amt": p1_amt, "q_amt": total_amount, "terms": plan_type, "ratios": ratios_str,
                                "desc": project_desc, "prog": "工程備料中 / 準備施工", "due": d1
                            }
                        )
                        conn.commit()
                st.success(L["create_success"])
                st.rerun()
            else:
                st.warning(L["fill_warning"])

def show(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def main(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)

def render_sales_order_ar(*args, **kwargs):
    render_sales_order_ar_page(*args, **kwargs)
