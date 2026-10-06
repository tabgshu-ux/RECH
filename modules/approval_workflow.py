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
        "warning_reject": "⚠️️ 已將單據 [{id}] 駁回並退給申請人。",
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
        "status_pending": "待審核",
        "status_approved": "已核准",
        "status_rejected": "已駁回"
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
        "status_pending": "Chờ duyệt",
        "status_approved": "Đã duyệt",
        "status_rejected": "Từ chối"
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
        "status_pending": "Pending",
        "status_approved": "Approved",
        "status_rejected": "Rejected"
    }
}

# ----------------------------------------------------
# 🔄 簽核模組專用：中越英智慧語意對照引擎
# ----------------------------------------------------
def smart_translate_approval(text_val, target_lang):
    if not text_val or not isinstance(text_val, str):
        return text_val
    
    val_lower = text_val.lower()

    if "待審核" in text_val or "pending" in val_lower or "chờ duyệt" in val_lower:
        if target_lang == "Tiếng Việt": return "Chờ duyệt"
        elif target_lang == "English": return "Pending"
        return "⏳ 待審核"
    if "已核准" in text_val or "approved" in val_lower or "đã duyệt" in val_lower:
        if target_lang == "Tiếng Việt": return "Đã duyệt"
        elif target_lang == "English": return "Approved"
        return "✅ 已核准"
    if "已駁回" in text_val or "rejected" in val_lower or "từ chối" in val_lower:
        if target_lang == "Tiếng Việt": return "Từ chối"
        elif target_lang == "English": return "Rejected"
        return "❌ 已駁回"

    return text_val

def render_approval_center(lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = APPROVAL_I18N.get(active_lang, APPROVAL_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    current_user = st.session_state.get("user_name", "Staff")
    current_role = st.session_state.get("user_role", "staff").lower()

    # 初始化簽核表單資料庫
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
        st.markdown(f"### {L['pending_header']} (當前登入: `{current_user}` | 角色: `{current_role.upper()}`)")
        
        pending_items = [item for item in st.session_state.approval_tasks_db if item["status"] == "待審核"]

        if not pending_items:
            st.success(L["no_pending"])
        else:
            for item in pending_items:
                with st.container():
                    st.markdown(
                        f"""
                        <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #cbd5e1; margin-bottom: 12px;">
                            <div style="font-size: 13px; color: #64748b; font-weight: 700;">📂 類別: {item['category']} | 編號: <code>{item['id']}</code></div>
                            <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin-top: 4px;">📌 {item['title']}</div>
                            <div style="font-size: 14px; color: #334155; margin-top: 6px;">
                                • <b>申請人</b>: {item['applicant']} &nbsp;|&nbsp; <b>日期</b>: {item['date']} &nbsp;|&nbsp; <b>金額</b>: <span style="color: #047857; font-weight:bold;">{item['amount']}</span><br>
                                • <b>內容</b>: {item['details']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
                    with col_btn1:
                        if st.button(L["btn_approve"], type="primary", key=f"approve_{item['id']}"):
                            item["status"] = "已核准"
                            st.success(L["success_approve"].format(id=item['id']))
                            st.rerun()
                    with col_btn2:
                        if st.button(L["btn_reject"], key=f"reject_{item['id']}"):
                            item["status"] = "已駁回"
                            st.warning(L["warning_reject"].format(id=item['id']))
                            st.rerun()
                    st.markdown("<br>", unsafe_allow_html=True)

    with tab_history:
        st.markdown(f"### {L['history_header']}")
        history_data = []
        for item in st.session_state.approval_tasks_db:
            history_data.append({
                "編號": item["id"],
                "類別": item["category"],
                "主旨": item["title"],
                "申請人": item["applicant"],
                "日期": item["date"],
                "金額": item["amount"],
                "狀態": smart_translate_approval(item["status"], active_lang)
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

            details = st.text_area(L["lbl_details"], value="因個人因素申請...")

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
                    st.success(L["success_submit"].format(new_id=new_id))
                    st.rerun()
                else:
                    st.warning(L["fill_warning"])

def show(lang="繁體中文", **kwargs):
    render_approval_center(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_approval_center(lang, **kwargs)
