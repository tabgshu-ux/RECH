import streamlit as st
import pandas as pd

def render_approval_center(engine=None, lang="繁體中文", **kwargs):
    # 多語言字典
    texts = {
        "繁體中文": {
            "title": "✍️ 全公司電子簽核與請款/請假審核中心",
            "info": "提交採購申請或請假單，系統自動依據規則進行多級簽核，並提供即時進度追蹤。",
            "tab1": "✍️ 員工請假申請單",
            "tab2": "🛒 採購與請款申請單",
            "tab3": "📊 簽核進度即時追蹤",
            "tab4": "🛃 待簽核案件審查",
            "form1_title": "### 📝 填寫請假申請單",
            "applicant": "申請人 (已鎖定登入帳號)",
            "dept": "所屬部門 (依帳號自動對應)",
            "days": "請假天數 (天) *",
            "reason": "申請事由與說明 *",
            "reason_ph": "例如: 因家庭事務請假 4 天...",
            "submit_btn": "🚀 提交送出簽核",
            "success_msg": "✅ 請假申請已成功提交並進入電子簽核流程！"
        },
        "Tiếng Việt": {
            "title": "✍️ Trung tâm Phê duyệt Điện tử & Quản lý Nghỉ phép/Thanh toán",
            "info": "Gửi đơn mua hàng hoặc xin nghỉ phép, hệ thống tự động phê duyệt đa cấp và theo dõi tiến độ thời gian thực.",
            "tab1": "✍️ Đơn xin nghỉ phép",
            "tab2": "🛒 Đơn mua hàng & Thanh toán",
            "tab3": "📊 Theo dõi tiến độ phê duyệt",
            "tab4": "🛃 Xét duyệt chờ xử lý",
            "form1_title": "### 📝 Điền đơn xin nghỉ phép",
            "applicant": "Người nộp đơn (Tài khoản đăng nhập)",
            "dept": "Phòng ban trực thuộc",
            "days": "Số ngày nghỉ (ngày) *",
            "reason": "Lý do & Mô tả chi tiết *",
            "reason_ph": "Ví dụ: Nghỉ việc gia đình 4 ngày...",
            "submit_btn": "🚀 Gửi yêu cầu phê duyệt",
            "success_msg": "✅ Đơn xin nghỉ phép đã được gửi thành công vào hệ thống phê duyệt!"
        },
        "English": {
            "title": "✍️ E-Approval Center for Leave & Procurement",
            "info": "Submit leave requests or purchase orders with automated multi-level approval workflows and real-time tracking.",
            "tab1": "✍️ Submit Leave Request",
            "tab2": "🛒 Purchase & Payment Request",
            "tab3": "📊 Real-time Approval Tracking",
            "tab4": "🛃 Pending Approvals Review",
            "form1_title": "### 📝 Leave Application Form",
            "applicant": "Applicant (Logged-in Account)",
            "dept": "Department",
            "days": "Leave Days *",
            "reason": "Reason & Description *",
            "reason_ph": "e.g., Family affairs for 4 days...",
            "submit_btn": "🚀 Submit for Approval",
            "success_msg": "✅ Leave application submitted successfully and entered the approval workflow!"
        }
    }

    t_set = texts.get(lang, texts["繁體中文"])

    st.title(t_set["title"])
    st.info(t_set["info"])

    if "approval_db" not in st.session_state:
        st.session_state.approval_db = [
            {
                "單號": "APV-2026-001", "類型": "請假單", "申請人": "admin", "部門": "總經理室", 
                "內容": "家庭事務請假 3 天", "狀態": "簽核中 (Pending)", "送出時間": "2026-10-07"
            }
        ]

    tab1, tab2, tab3, tab4 = st.tabs([t_set["tab1"], t_set["tab2"], t_set["tab3"], t_set["tab4"]])

    with tab1:
        with st.form("leave_application_form"):
            st.markdown(t_set["form1_title"])
            c1, c2 = st.columns(2)
            with c1:
                st.text_input(t_set["applicant"], value=st.session_state.get("user_name", "admin"), disabled=True, key="lev_user")
            with c2:
                st.text_input(t_set["dept"], value="總經理室 / Executive Office", disabled=True, key="lev_dept")

            leave_days = st.number_input(t_set["days"], min_value=0.5, value=3.0, step=0.5, key="lev_days")
            leave_reason = st.text_area(t_set["reason"], placeholder=t_set["reason_ph"], key="lev_reason")

            if st.form_submit_button(t_set["submit_btn"], type="primary"):
                if leave_reason:
                    new_no = f"APV-2026-{len(st.session_state.approval_db)+1:03d}"
                    st.session_state.approval_db.append({
                        "單號": new_no,
                        "類型": "請假單 (Leave)",
                        "申請人": st.session_state.get("user_name", "admin"),
                        "部門": "總經理室",
                        "內容": f"請假 {leave_days} 天: {leave_reason}",
                        "狀態": "簽核中 (Pending)",
                        "送出時間": "2026-10-08"
                    })
                    st.success(t_set["success_msg"])
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫申請事由！")

    with tab2:
        st.markdown("### 🛒 採購與請款申請單 (Purchase & Payment Request)")
        with st.form("purchase_approval_form"):
            p_item = st.text_input("採購項目 / 品名 (Item Name) *", placeholder="例如: 變壓器 / 零件...")
            p_amt = st.number_input("預估金額 (Estimated Amount VND)", value=5000000.0, step=100000.0)
            p_desc = st.text_area("採購用途與必要性說明", placeholder="請說明採購原因...")
            if st.form_submit_button("🚀 提交採購請款簽核", type="primary"):
                if p_item:
                    new_no = f"APV-2026-{len(st.session_state.approval_db)+1:03d}"
                    st.session_state.approval_db.append({
                        "單號": new_no,
                        "類型": "採購請款",
                        "申請人": st.session_state.get("user_name", "admin"),
                        "部門": "工程與設計管理中心",
                        "內容": f"採購 {p_item}, 金額: {p_amt:,.0f} VND",
                        "狀態": "簽核中 (Pending)",
                        "送出時間": "2026-10-08"
                    })
                    st.success("✅ 採購申請已送出！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請填寫採購品名！")

    with tab3:
        st.markdown("### 📊 全公司簽核進度即時追蹤 (Real-time Tracking)")
        if st.session_state.approval_db:
            st.dataframe(pd.DataFrame(st.session_state.approval_db), use_container_width=True)
        else:
            st.info("目前無任何簽核案件記錄。")

    with tab4:
        st.markdown("### 🛃 主管待簽核案件審查 (Pending Review)")
        st.info("主管/高階管理層可在此審核轄下員工之請假與採購申請。")
        if st.session_state.approval_db:
            for idx, item in enumerate(st.session_state.approval_db):
                if "簽核中" in item["狀態"]:
                    with st.expander(f"📌 [{item['單號']}] {item['類型']} - 申請人: {item['申請人']} ({item['內容']})"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"✅ 核准 (Approve)", key=f"app_{idx}"):
                                item["狀態"] = "已核准 (Approved)"
                                st.success(f"✅ 已核准單號 {item['單號']}")
                                st.rerun()
                        with col_b:
                            if st.button(f"❌ 駁回 (Reject)", key=f"rej_{idx}"):
                                item["狀態"] = "已駁回 (Rejected)"
                                st.warning(f"❌ 已駁回單號 {item['單號']}")
                                st.rerun()
        else:
            st.info("目前沒有需要您審核的待辦案件。")

def render_approval_center_page(*args, **kwargs):
    render_approval_center(*args, **kwargs)

def show(*args, **kwargs):
    render_approval_center(*args, **kwargs)

def main(*args, **kwargs):
    render_approval_center(*args, **kwargs)
