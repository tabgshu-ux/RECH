import pandas as pd
import streamlit as st

# 🌐 多語系字典 (i18n)
APPROVAL_I18N = {
    "繁體中文": {
        "page_title": "📄 企業 AI 簽核與表單審核中心",
        "sub_title": "跨部門表單簽核關卡、待辦清單與歷史簽核履歷管理",
        "metric_pending": "⏳ 我的待簽核單據",
        "metric_approved": "🟢 本月已核准單據",
        "metric_rejected": "🔴 已駁回/退回單據",
        "unit_count": "筆",
        "action_needed": "⚡ 需處理",
        "section_pending": "📥 待審核單據列表",
        "lbl_apply_date": "申請日期",
        "lbl_applicant": "申請人",
        "lbl_module": "來源模組",
        "lbl_detail": "申請詳情",
        "lbl_amount": "金額",
        "btn_approve": "✅ 核准通過",
        "btn_reject": "❌ 退回駁回",
        "msg_approved": "已順利核准單據！",
        "msg_rejected": "已駁回單據。",
        "empty_pending": "🎉 目前沒有等待您簽核的單據。",
    },
    "Tiếng Việt": {
        "page_title": "📄 Trung tâm Phê duyệt & Ký duyệt Điện tử AI",
        "sub_title": "Quản lý quy trình ký duyệt liên phòng ban, danh sách chờ duyệt và lịch sử ký duyệt.",
        "metric_pending": "⏳ Đơn hàng chờ tôi duyệt",
        "metric_approved": "🟢 Đơn đã duyệt trong tháng",
        "metric_rejected": "🔴 Đơn đã từ chối / Trả về",
        "unit_count": "đơn",
        "action_needed": "⚡ Cần xử lý",
        "section_pending": "📥 Danh sách Đơn hàng Chờ Phê duyệt",
        "lbl_apply_date": "Ngày yêu cầu",
        "lbl_applicant": "Người yêu cầu",
        "lbl_module": "Phòng ban / Nguồn",
        "lbl_detail": "Chi tiết yêu cầu",
        "lbl_amount": "Số tiền",
        "btn_approve": "✅ Phê duyệt (Duyệt)",
        "btn_reject": "❌ Từ chối (Trả về)",
        "msg_approved": "Đã phê duyệt đơn thành công!",
        "msg_rejected": "Đã từ chối đơn thành công!",
        "empty_pending": "🎉 Hiện tại không có đơn hàng nào chờ bạn phê duyệt.",
    },
    "English": {
        "page_title": "📄 Enterprise AI E-Approval Center",
        "sub_title": "Cross-department approval workflows, pending list, and history audit trail.",
        "metric_pending": "⏳ Pending My Approval",
        "metric_approved": "🟢 Approved This Month",
        "metric_rejected": "🔴 Rejected / Returned",
        "unit_count": "items",
        "action_needed": "⚡ Action Required",
        "section_pending": "📥 Pending Documents for Approval",
        "lbl_apply_date": "Request Date",
        "lbl_applicant": "Applicant",
        "lbl_module": "Source Module",
        "lbl_detail": "Details",
        "lbl_amount": "Amount",
        "btn_approve": "✅ Approve",
        "btn_reject": "❌ Reject",
        "msg_approved": "Document approved successfully!",
        "msg_rejected": "Document rejected successfully!",
        "empty_pending": "🎉 No pending documents waiting for your approval.",
    },
}


def render_approval_center(*args, **kwargs):
    # 自動讀取全局語系設定
    lang = (
        kwargs.get("lang")
        or kwargs.get("curr_lang")
        or st.session_state.get("current_lang", "繁體中文")
    )
    L = APPROVAL_I18N.get(lang, APPROVAL_I18N["繁體中文"])

    st.title(L["page_title"])
    st.caption(L["sub_title"])

    if "approval_tasks" not in st.session_state:
        st.session_state.approval_tasks = [
            {
                "id": "APV-20260926-01",
                "module": "總務部 - 零用金",
                "applicant": "李大同",
                "date": "2026-09-25",
                "desc": "拜訪客戶計程車費 ($45.0 USD)",
                "status": "待審核",
            },
            {
                "id": "APV-20260926-02",
                "module": "採購部 - 廠商發票",
                "applicant": "陳美麗",
                "date": "2026-09-26",
                "desc": "西寧廠塗裝粉體原料採購請款 ($12,500 USD)",
                "status": "待審核",
            },
        ]

    pending_items = [
        item
        for item in st.session_state.approval_tasks
        if item["status"] == "待審核"
    ]
    approved_items = [
        item
        for item in st.session_state.approval_tasks
        if item["status"] == "已核准"
    ]
    rejected_items = [
        item
        for item in st.session_state.approval_tasks
        if item["status"] == "已駁回"
    ]

    m1, m2, m3 = st.columns(3)
    m1.metric(
        L["metric_pending"],
        f"{len(pending_items)} {L['unit_count']}",
        L["action_needed"] if len(pending_items) > 0 else "0",
    )
    m2.metric(L["metric_approved"], f"{len(approved_items)} {L['unit_count']}")
    m3.metric(L["metric_rejected"], f"{len(rejected_items)} {L['unit_count']}")

    st.markdown("---")
    st.markdown(f"### {L['section_pending']}")

    if not pending_items:
        st.info(L["empty_pending"])
    else:
        for item in pending_items:
            with st.expander(
                f"📄 [{item['id']}] {item['module']} - {item['desc']}",
                expanded=True,
            ):
                c1, c2 = st.columns(2)
                c1.write(f"**{L['lbl_apply_date']}**: {item['date']}")
                c1.write(f"**{L['lbl_applicant']}**: {item['applicant']}")
                c2.write(f"**{L['lbl_module']}**: {item['module']}")
                c2.write(f"**{L['lbl_detail']}**: {item['desc']}")

                btn_col1, btn_col2, _ = st.columns([1, 1, 3])
                if btn_col1.button(
                    L["btn_approve"], key=f"app_{item['id']}", type="primary"
                ):
                    item["status"] = "已核准"
                    st.success(f"{item['id']} {L['msg_approved']}")
                    st.rerun()

                if btn_col2.button(
                    L["btn_reject"], key=f"rej_{item['id']}"
                ):
                    item["status"] = "已駁回"
                    st.error(f"{item['id']} {L['msg_rejected']}")
                    st.rerun()


def show(*args, **kwargs):
    render_approval_center(*args, **kwargs)


def main(*args, **kwargs):
    render_approval_center(*args, **kwargs)
