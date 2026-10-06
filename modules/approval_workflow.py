import pandas as pd
import streamlit as st

# ----------------------------------------------------
# 🌐 電子簽核與審核中心模組多語系字典 (i18n)
# ----------------------------------------------------
APPROVAL_I18N = {
    "繁體中文": {
        "title": "✍️ 管理部 - 電子簽核與請款審核中心",
        "caption": "跨部門電子流程審核：涵蓋請假、採購、合約、請款、借款與資產報廢等全方位簽核。",
        "tab_pending": "📥 待審核清單 (Pending)",
        "tab_history": "📜 歷史簽核紀錄 (History)",
        "tab_new": "➕ 提交新簽核申請 (Submit)",
        "pending_header": "📥 待審核項目列表",
        "no_pending": "🎉 目前沒有需要您審核的待辦事項！",
        "btn_approve": "✅ 核准簽核",
        "btn_reject": "❌ 駁回退回",
        "success_approve": "🎉 已成功核准單據 [{id}]！",
        "warning_reject": "⚠️ 已將單據 [{id}] 駁回並退給申請人。",
        "history_header": "📜 歷史簽核與歸檔紀錄",
        "new_header": "➕ 提交跨部門電子簽核申請",
        "lbl_category": "選擇簽核項目類別 *",
        "cat_opts": [
            "🌴 人事行政 - 員工請假/加班單",
            "💰 財務採購 - 採購單與請款單 (AP)",
            "📜 業務合約 - 客戶報價與工程合約",
            "💳 財務行政 - 員工借款/預支薪資申請",
            "🛠️ 工務技術 - 設計變更與驗收單",
            "📦 生產總務 - 設備報廢與資產購置",
        ],
        "lbl_title": "簽核主旨標題 *",
        "title_default": "西寧廠新進技術員請假單",
        "lbl_amount": "涉及金額 / 數量 (若無填 -)",
        "lbl_applicant": "申請人姓名與職稱 *",
        "lbl_details": "填寫詳細事由與說明 *",
        "btn_submit": "🚀 提交送出電子簽核",
        "success_submit": "🎉 簽核單 [{new_id}] 已成功提交並發送給部門主管與管理中心！",
        "fill_warning": "請完整填寫主旨與詳細事由！",
        "lbl_cat_card": "📂 類別",
        "lbl_id": "編號",
        "lbl_applicant_card": "申請人",
        "lbl_date_card": "申請日期",
        "lbl_amount_card": "金額/影響",
        "lbl_details_card": "內容細節",
        "login_info": "📥 待審核項目列表 (當前登入: `{user}` | 角色: `{role}`)"
    },
    "Tiếng Việt": {
        "title": "✍️ Khối Quản lý - Trung tâm Phê duyệt Điện tử",
        "caption": "Phê duyệt quy trình điện tử liên bộ phận: xin nghỉ phép, mua hàng, hợp đồng, thanh toán và thanh lý tài sản.",
        "tab_pending": "📥 Danh sách Chờ duyệt (Pending)",
        "tab_history": "📜 Lịch sử Phê duyệt (History)",
        "tab_new": "➕ Gửi Yêu cầu Phê duyệt Mới",
        "pending_header": "📥 Danh sách chờ phê duyệt",
        "no_pending": "🎉 Hiện không có hạng mục nào cần bạn phê duyệt!",
        "btn_approve": "✅ Phê duyệt",
        "btn_reject": "❌ Từ chối",
        "success_approve": "🎉 Đã phê duyệt thành công chứng từ [{id}]!",
        "warning_reject": "⚠️ Đã từ chối chứng từ [{id}] và trả về cho người yêu cầu.",
        "history_header": "📜 Lịch sử phê duyệt & Lưu trữ",
        "new_header": "➕ Gửi đơn xin phê duyệt điện tử",
        "lbl_category": "Chọn loại phê duyệt *",
        "cat_opts": [
            "🌴 Nhân sự - Đơn xin nghỉ phép / tăng ca",
            "💰 Tài chính - Đơn mua hàng & thanh toán (AP)",
            "📜 Kinh doanh - Báo giá & Hợp đồng dự án",
            "💳 Tài chính - Tạm ứng lương / Khoản vay",
            "🛠️ Kỹ thuật - Thay đổi thiết kế & Nghiệm thu",
            "📦 Hành chính - Thanh lý thiết bị & Mua sắm",
        ],
        "lbl_title": "Tiêu đề nội dung *",
        "title_default": "Đơn xin nghỉ phép kỹ thuật viên nhà máy Tây Ninh",
        "lbl_amount": "Số tiền / Số lượng liên quan",
        "lbl_applicant": "Họ tên & Chức vụ người nộp *",
        "lbl_details": "Nội dung chi tiết & Lý do *",
        "btn_submit": "🚀 Gửi yêu cầu phê duyệt",
        "success_submit": "🎉 Đơn phê duyệt [{new_id}] đã được gửi thành công đến quản lý!",
        "fill_warning": "Vui lòng điền đầy đủ tiêu đề và nội dung chi tiết!",
        "lbl_cat_card": "📂 Phân loại",
        "lbl_id": "Mã số",
        "lbl_applicant_card": "Người nộp",
        "lbl_date_card": "Ngày nộp",
        "lbl_amount_card": "Số tiền",
        "lbl_details_card": "Chi tiết",
        "login_info": "📥 Danh sách chờ duyệt (Đăng nhập: `{user}` | Quyền: `{role}`)"
    },
    "English": {
        "title": "✍️ Admin - E-Approval & Payment Review Center",
        "caption": "Cross-departmental electronic approvals covering leave requests, procurement, contracts, payments, and asset disposal.",
        "tab_pending": "📥 Pending Approvals",
        "tab_history": "📜 Approval History",
        "tab_new": "➕ Submit New Request",
        "pending_header": "📥 Pending Approval Items",
        "no_pending": "🎉 No pending items require your review!",
        "btn_approve": "✅ Approve",
        "btn_reject": "❌ Reject",
        "success_approve": "🎉 Successfully approved document [{id}]!",
        "warning_reject": "⚠️ Document [{id}] has been rejected and returned.",
        "history_header": "📜 Approval History & Archives",
        "new_header": "➕ Submit Cross-Departmental E-Approval",
        "lbl_category": "Select Request Category *",
        "cat_opts": [
            "🌴 HR - Leave / Overtime Request",
            "💰 Finance - Procurement & AP Invoice",
            "📜 Sales - Quotation & Engineering Contract",
            "💳 Finance - Employee Advance / Loan",
            "🛠️ Engineering - Design Change & Inspection",
            "📦 GA - Asset Disposal & Procurement",
        ],
        "lbl_title": "Subject Title *",
        "title_default": "Leave Request for Tay Ninh Technician",
        "lbl_amount": "Amount / Quantity",
        "lbl_applicant": "Applicant Name & Title *",
        "lbl_details": "Detailed Description *",
        "btn_submit": "🚀 Submit E-Approval",
        "success_submit": "🎉 Approval request [{new_id}] successfully submitted!",
        "fill_warning": "Please fill in the title and detailed description!",
        "lbl_cat_card": "📂 Category",
        "lbl_id": "ID",
        "lbl_applicant_card": "Applicant",
        "lbl_date_card": "Date",
        "lbl_amount_card": "Amount",
        "lbl_details_card": "Details",
        "login_info": "📥 Pending Approval List (User: `{user}` | Role: `{role}`)"
    }
}

def smart_translate_approval_content(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    if target_lang == "Tiếng Việt":
        if "越南西寧廠技術員事假 2 天" in text_val: return "Nghỉ phép 2 ngày của kỹ thuật viên nhà máy Tây Ninh"
        if "因家屬探親請假 2 天" in text_val: return "Xin nghỉ 2 ngày thăm người thân (đã sắp xếp người thay thế)"
        if "西寧廠塗裝粉體原料採購款" in text_val: return "Thanh toán mua nguyên liệu sơn tĩnh điện nhà máy Tây Ninh"
        if "採購環保靜電粉末塗料 500 公斤" in text_val: return "Mua 500kg bột sơn tĩnh điện thân thiện môi trường"
    elif target_lang == "English":
        if "越南西寧廠技術員事假 2 天" in text_val: return "Tay Ninh Plant Technician 2-Day Leave"
        if "因家屬探親請假 2 天" in text_val: return "Family visit leave for 2 days (backup arranged)"
        if "西寧廠塗裝粉體原料採購款" in text_val: return "Tay Ninh Plant Powder Coating Material Purchase"
        if "採購環保靜電粉末塗料 500 公斤" in text_val: return "Purchase 500kg eco-friendly electrostatic coating powder"

    return text_val

def render_approval_center(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = APPROVAL_I18N.get(active_lang, APPROVAL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    current_user = st.session_state.get("user_name", "Staff")
    current_role = st.session_state.get("user_role", "staff").lower()

    if "approval_tasks_db" not in st.session_state or not st.session_state.approval_tasks_db:
        st.session_state.approval_tasks_db = [
            {
                "id": "APP-2026-001",
                "category": "🌴 人事行政 - 員工請假申請",
                "title": "越南西寧廠技術員事假 2 天",
                "applicant": "Nguyễn Văn An (Staff)",
                "date": "2026-10-02",
                "amount": "-",
                "details": "因家屬探親請假 2 天 (已安排職務代理人)",
                "status": "待審核",
            },
            {
                "id": "APP-2026-002",
                "category": "💰 財務採購 - 採購與請款單",
                "title": "西寧廠塗裝粉體原料採購款",
                "applicant": "陳美璇 (Finance Staff)",
                "date": "2026-10-02",
                "amount": "$12,500 USD",
                "details": "採購環保靜電粉末塗料 500 公斤",
                "status": "待審核",
            }
        ]

    tab_pending, tab_history, tab_new = st.tabs([
        L["tab_pending"], L["tab_history"], L["tab_new"]
    ])

    with tab_pending:
        st.markdown(f"### {L['login_info'].format(user=current_user, role=current_role.upper())}")
        
        pending_items = [item for item in st.session_state.approval_tasks_db if item["status"] == "待審核"]

        if not pending_items:
            st.success(L["no_pending"])
        else:
            for item in pending_items:
                card_title = smart_translate_approval_content(item['title'], active_lang)
                card_details = smart_translate_approval_content(item['details'], active_lang)

                with st.container():
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 12px;">
                            <div style="font-size: 13px; color: #64748b; font-weight: 700;">{L['lbl_cat_card']}: {item['category']} | {L['lbl_id']}: <code>{item['id']}</code></div>
                            <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin-top: 4px;">📌 {card_title}</div>
                            <div style="font-size: 14px; color: #334155; margin-top: 6px;">
                                • <b>{L['lbl_applicant_card']}</b>: {item['applicant']} &nbsp;|&nbsp; <b>{L['lbl_date_card']}</b>: {item['date']} &nbsp;|&nbsp; <b>{L['lbl_amount_card']}</b>: <span style="color: #047857; font-weight:bold;">{item['amount']}</span><br>
                                • <b>{L['lbl_details_card']}</b>: {card_details}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
                    with col_btn1:
                        if st.button(L["btn_approve"], type="primary", key=f"approve_{item['id']}"):
                            item["status"] = "已核准"
                            st.success(f"🎉 Approved [{item['id']}]！")
                            st.rerun()
                    with col_btn2:
                        if st.button(L["btn_reject"], key=f"reject_{item['id']}"):
                            item["status"] = "已駁回"
                            st.warning(f"⚠️ Rejected [{item['id']}].")
                            st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)

    with tab_history:
        st.markdown(f"### {L['history_header']}")
        history_data = []
        for item in st.session_state.approval_tasks_db:
            history_data.append({
                "ID": item["id"],
                "Category": item["category"],
                "Title": smart_translate_approval_content(item["title"], active_lang),
                "Applicant": item["applicant"],
                "Date": item["date"],
                "Amount": item["amount"],
                "Status": item["status"]
            })
        st.dataframe(pd.DataFrame(history_data), use_container_width=True)

    with tab_new:
        st.markdown(f"### {L['new_header']}")
        with st.form("form_submit_approval"):
            c1, c2 = st.columns(2)
            with c1:
                category = st.selectbox(L["lbl_category"], L["cat_opts"])
                title = st.text_input(L["lbl_title"], value=L["title_default"])
            with c2:
                amount = st.text_input(L["lbl_amount"], value="-")
                applicant = st.text_input(L["lbl_applicant"], value=f"{current_user} ({current_role.upper()})")

            details = st.text_area(L["lbl_details"], value="...")

            if st.form_submit_button(L["btn_submit"], type="primary", use_container_width=True):
                if title and details:
                    new_id = f"APP-2026-{len(st.session_state.approval_tasks_db)+1:03d}"
                    st.session_state.approval_tasks_db.append({
                        "id": new_id,
                        "category": category,
                        "title": title,
                        "applicant": applicant,
                        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                        "amount": amount,
                        "details": details,
                        "status": "待審核",
                    })
                    st.success(f"🎉 Success [{new_id}]！")
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

def show(lang="繁體中文", **kwargs):
    render_approval_center(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_approval_center(lang, **kwargs)
