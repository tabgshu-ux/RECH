import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 🌐 應收帳款與專案進度模組多語系字典 (i18n)
# ----------------------------------------------------
AR_I18N = {
    "繁體中文": {
        "title": "📋 管理部 - 客戶應收帳款 (AR) & 專案分期進度管理",
        "caption": "記錄客戶工程合約總額、動態分期付款排程管理、專案說明與進度實時追蹤。",
        "tab_list": "📑 客戶應收款項總表與進度",
        "tab_edit": "✍️ 修改進行進度說明與催收歷程",
        "tab_add": "➕ 登記新應收帳款專案",
        # 頁籤一
        "table_header": "📋 客戶應收帳款專案清冊",
        "no_records": "目前無應收帳款紀錄。",
        "read_error": "讀取資料失敗: ",
        # 頁籤二
        "edit_header": "✍️ 修改專案進行進度說明與催收紀錄",
        "select_project": "請選擇要更新進度的請款專案：",
        "current_project": "當前專案",
        "total_amount_label": "總帳款",
        "new_progress_label": "更新「進行進度說明」*",
        "new_reason_label": "更新/追加「催收理由與客戶回應」",
        "modifier_label": "修改人員姓名*",
        "save_update_btn": "💾 儲存並更新專案進度",
        "update_success": "請款單 `{target_id}` 之進行進度與催收理由已更新！",
        # 頁籤三
        "add_header": "➕ 登記新應收帳款專案",
        "inv_id_label": "請款編號 *",
        "entity_name_label": "客戶名稱 *",
        "entity_placeholder": "越南樟榜工業區A廠",
        "project_name_label": "工程名稱 *",
        "project_placeholder": "西寧廠 2000A 配電櫃新建工程",
        "currency_label": "交易幣別 *",
        "usd_label": "總帳款 (USD - 精確至小數點後 3 位) *",
        "total_lbl": "總帳款 *",
        "plan_type_label": "付款期數模式 *",
        "proj_desc_label": "專案說明",
        "proj_desc_placeholder": "請填寫本工程施工內容與合約細節...",
        "progress_note_label": "進行進度說明",
        "milestone_header": "💳 分期百分比 (%) 與付款日期細項設定",
        "single_pay_info": "全額一次付清：",
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
        "fill_warning": "⚠️ 請完整填寫客戶名稱與工程名稱！"
    },
    "Tiếng Việt": {
        "title": "📋 Khối Quản lý - Phải thu Khách hàng (AR) & Tiến độ Dự án",
        "caption": "Quản lý tổng số tiền hợp đồng, lịch trình thanh toán theo đợt, cập nhật tiến độ.",
        "tab_list": "📑 Danh sách Phải thu & Tiến độ",
        "tab_edit": "✍️ Cập nhật Tiến độ & Lý do thu nợ",
        "tab_add": "➕ Thêm Dự án Phải thu Mới",
        # 頁籤一
        "table_header": "📋 Sổ chi tiết Phải thu Khách hàng",
        "no_records": "Hiện không có bản ghi khoản phải thu nào.",
        "read_error": "Lỗi đọc dữ liệu: ",
        # 頁籤二
        "edit_header": "✍️ Sửa đổi tiến độ dự án và ghi chú thu nợ",
        "select_project": "Chọn dự án cần cập nhật tiến độ:",
        "current_project": "Dự án hiện tại",
        "total_amount_label": "Tổng tiền",
        "new_progress_label": "Cập nhật \"Mô tả tiến độ\" *",
        "new_reason_label": "Cập nhật/Bổ sung \"Lý do thu nợ & phản hồi từ khách hàng\"",
        "modifier_label": "Họ tên người sửa*",
        "save_update_btn": "💾 Lưu và cập nhật tiến độ dự án",
        "update_success": "Đã cập nhật tiến độ và lý do thu nợ cho hóa đơn `{target_id}`!",
        # 頁籤三
        "add_header": "➕ Đăng ký dự án khoản phải thu mới",
        "inv_id_label": "Mã hóa đơn / khoản thu *",
        "entity_name_label": "Tên khách hàng *",
        "entity_placeholder": "Nhà máy A KCN Trảng Bàng, Tây Ninh",
        "project_name_label": "Tên công trình *",
        "project_placeholder": "Lắp đặt tủ điện 2000A nhà máy Tây Ninh",
        "currency_label": "Loại tiền tệ *",
        "usd_label": "Tổng tiền (USD - Chính xác đến 3 chữ số thập phân) *",
        "total_lbl": "Tổng tiền *",
        "plan_type_label": "Hình thức thanh toán *",
        "proj_desc_label": "Mô tả dự án",
        "proj_desc_placeholder": "Nhập nội dung thi công và chi tiết hợp đồng...",
        "progress_note_label": "Mô tả tiến độ",
        "milestone_header": "💳 Thiết lập tỷ lệ phần trăm (%) và ngày thanh toán theo đợt",
        "single_pay_info": "Thanh toán 100% một lần:",
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
        "fill_warning": "⚠️ Vui lòng điền đầy đủ Tên khách hàng và Tên công trình!"
    },
    "English": {
        "title": "📋 Admin - Accounts Receivable (AR) & Project Installments",
        "caption": "Track total contract amounts, installment schedules, descriptions, and progress updates.",
        "tab_list": "📑 AR Summary & Progress",
        "tab_edit": "✍️ Update Progress & Collection Audit",
        "tab_add": "➕ Register New AR Project",
        # 頁籤一
        "table_header": "📋 Customer Accounts Receivable Registry",
        "no_records": "No accounts receivable records found.",
        "read_error": "Failed to read data: ",
        # 頁籤二
        "edit_header": "✍️ Modify Project Progress & Collection Log",
        "select_project": "Select project to update:",
        "current_project": "Current Project",
        "total_amount_label": "Total Amount",
        "new_progress_label": "Update Progress Description *",
        "new_reason_label": "Update/Append Collection Remarks & Client Feedback",
        "modifier_label": "Modifier Name *",
        "save_update_btn": "💾 Save & Update Project Progress",
        "update_success": "Progress and collection reasons for invoice `{target_id}` updated successfully!",
        # 頁籤三
        "add_header": "➕ Register New Accounts Receivable Project",
        "inv_id_label": "Invoice ID *",
        "entity_name_label": "Client Name *",
        "entity_placeholder": "Tay Ninh Plant Client A",
        "project_name_label": "Project Name *",
        "project_placeholder": "Tay Ninh 2000A Switchboard Installation",
        "currency_label": "Currency *",
        "usd_label": "Total Amount (USD - 3 decimal places) *",
        "total_lbl": "Total Amount *",
        "plan_type_label": "Payment Terms *",
        "proj_desc_label": "Project Description",
        "proj_desc_placeholder": "Enter construction scope and contract details...",
        "progress_note_label": "Progress Description",
        "milestone_header": "💳 Milestone Installment Percentage (%) & Due Dates",
        "single_pay_info": "Full payment in one lump sum:",
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
        "fill_warning": "⚠️ Please fill in Client Name and Project Name!"
    }
}

def format_curr(amt, curr):
    if curr == "越南盾": return f"₫ {amt:,.0f} VND"
    elif curr == "美金": return f"$ {amt:,.3f} USD"
    elif curr == "台幣": return f"NT$ {amt:,.0f} TWD"
    elif curr == "人民幣": return f"¥ {amt:,.2f} CNY"
    return f"{amt:,.3f} {curr}"

def render_sales_order_ar_page(engine=None, lang="繁體中文", **kwargs):
    # 支援動態從 session_state 或參數取得語系
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = AR_I18N.get(active_lang, AR_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_edit, tab_add = st.tabs([L["tab_list"], L["tab_edit"], L["tab_add"]])

    # 1. 應收帳款總覽清單
    with tab_list:
        st.subheader(L["table_header"])
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    display_list = []
                    for idx, r in df_ar.iterrows():
                        display_list.append({
                            "編號": idx + 1,
                            "請款編號": r.get("invoice_id"),
                            "客戶名稱": r.get("entity_name"),
                            "工程名稱": r.get("project_name"),
                            "交易幣別": r.get("currency"),
                            "總帳款": format_curr(r.get("quoted_amount", 0.0), r.get("currency")),
                            "分期類型": r.get("payment_terms", "不分期"),
                            "分期比率": r.get("installment_ratios", "100%"),
                            "進行進度說明": r.get("progress_note", "工程備料中"),
                            "專案說明": r.get("project_desc", "-"),
                            "最新催收理由/歷程": r.get("uncollected_reason", "-")
                        })
                    st.dataframe(pd.DataFrame(display_list), use_container_width=True)
                else:
                    st.info(L["no_records"])
            except Exception as e:
                st.error(f"{L['read_error']}{e}")

    # 2. 修改進行進度說明與催收歷程
    with tab_edit:
        st.subheader(L["edit_header"])
        if engine:
            try:
                df_ar = pd.read_sql("SELECT * FROM invoices WHERE invoice_type='AR'", engine)
                if not df_ar.empty:
                    ar_opts = {f"{r['invoice_id']} - {r['entity_name']} ({r['project_name']})": r['invoice_id'] for _, r in df_ar.iterrows()}
                    sel_label = st.selectbox(L["select_project"], list(ar_opts.keys()))
                    target_id = ar_opts[sel_label]
                    target_row = df_ar[df_ar['invoice_id'] == target_id].iloc[0]

                    st.markdown(f"**{L['current_project']}**：`{target_row['project_name']}` | **{L['total_amount_label']}**：{format_curr(target_row['quoted_amount'], target_row['currency'])}")
                    
                    with st.form("form_update_ar_progress"):
                        new_progress = st.text_area(L["new_progress_label"], value=target_row.get("progress_note", ""))
                        new_reason = st.text_area(L["new_reason_label"], value=target_row.get("uncollected_reason", ""))
                        modifier = st.text_input(L["modifier_label"], value=st.session_state.get("user_name", "admin"))

                        if st.form_submit_button(L["save_update_btn"], use_container_width=True):
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                            full_reason = f"【{timestamp} 修改人:{modifier}】{new_reason}"
                            
                            with engine.connect() as conn:
                                conn.execute(
                                    text("""
                                        UPDATE invoices 
                                        SET progress_note = :prog,
                                            uncollected_reason = :reason,
                                            quoter_name = :quoter
                                        WHERE invoice_id = :id
                                    """),
                                    {"prog": new_progress, "reason": full_reason, "quoter": modifier, "id": target_id}
                                )
                                conn.commit()
                            st.success(L["update_success"].format(target_id=target_id))
                            st.rerun()
            except Exception as e:
                st.error(f"{L['read_error']}{e}")

    # 3. 新增請款專案 (具備專業介面與自訂百分比)
    with tab_add:
        st.subheader(L["add_header"])
        
        c1, c2 = st.columns(2)
        with c1:
            inv_id = st.text_input(L["inv_id_label"], value=f"AR-2026-{datetime.datetime.now().strftime('%m%d%H%M')}")
            entity_name = st.text_input(L["entity_name_label"], placeholder=L["entity_placeholder"])
            project_name = st.text_input(L["project_name_label"], placeholder=L["project_placeholder"])
            currency = st.selectbox(L["currency_label"], ["越南盾", "美金", "台幣", "人民幣"])
            
            if currency == "美金":
                total_amount = st.number_input(L["usd_label"], min_value=0.0, value=10000.000, format="%.3f", step=0.001)
            else:
                total_amount = st.number_input(L["total_lbl"], min_value=0.0, value=100000.0, step=1000.0)

        with c2:
            plan_type = st.selectbox(L["plan_type_label"], ["不分期", "分三期", "分五期"])
            project_desc = st.text_area(L["proj_desc_label"], placeholder=L["proj_desc_placeholder"])
            progress_note = st.text_input(L["progress_note_label"], value="工程備料中 / 準備施工")

        st.markdown("---")
        st.markdown(f"##### {L['milestone_header']}")

        ratios_str = "100%"
        p1_amt, p2_amt, p3_amt, p4_amt, p5_amt = total_amount, 0.0, 0.0, 0.0, 0.0
        d1, d2, d3, d4, d5 = datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today(), datetime.date.today()

        if plan_type == "不分期":
            d1 = st.date_input("付款日期", value=datetime.date.today() + datetime.timedelta(days=30), key="ar_d_single")
            st.info(f"{L['single_pay_info']} {format_curr(total_amount, currency)}")

        elif plan_type == "分三期":
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                r1 = st.number_input("第 1 期比率 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r1")
            with col_r2:
                r2 = st.number_input("第 2 期比率 (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0, key="ar_3r2")
            with col_r3:
                r3 = st.number_input("第 3 期比率 (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0, key="ar_3r3")
            
            total_pct = r1 + r2 + r3
            if abs(total_pct - 100.0) > 0.01:
                st.warning(L["ratio_warning"].format(total_pct=total_pct))
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

        elif plan_type == "分五期":
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
                st.warning(L["ratio_warning"].format(total_pct=total_pct))
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
                d2 = st.date_input(L["period_2_date"], value=datetime.date.today() + datetime.timedelta(days=30), key
