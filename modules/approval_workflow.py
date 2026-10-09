# 在請假申請表單 (Leave Request Form) 的區段中：

st.markdown("#### 🍃 請請假申請單 (Leave Request)")

with st.form("leave_request_form"):
    lc1, lc2 = st.columns(2)
    with lc1:
        applicant_name = st.text_input("申請人姓名 (Applicant Name - 系統自動綁定)", value=f"{st.session_state.get('user_name', 'admin')} ({st.session_state.get('user_role', 'ADMIN').upper()})", disabled=True)
        leave_type = st.selectbox("請假類別 (Leave Type)", ["事假 (Personal Leave)", "病假 (Sick Leave)", "特休假 (Annual Leave)", "產假/婚喪假 (Maternity/Bereavement)"])
    with lc2:
        request_no = st.text_input("申請單編號 (Request No.)", value="REQ-2026-005", disabled=True)
        department = st.text_input("申請部門 (Department)", value="工程與設計管理中心 (Engineering Dept)", disabled=True)

    # ⏱️ 關鍵修改：將原本的「請假天數」改為「請假時數（以 0.5 小時/半小時為單位遞增）」
    leave_hours = st.number_input(
        "請假時數 (Hours) * 最小單位為 0.5 小時（半小時）", 
        min_value=0.5, 
        max_value=176.0, 
        value=8.0, 
        step=0.5,
        help="例如：請假半小時請輸入 0.5，請假 1 小時輸入 1.0，請假半天(4小時)輸入 4.0"
    )

    leave_reason = st.text_area("請假事由說明 (Reason)", placeholder="例如：個人私事或前往醫院看診，請假 1.5 小時。")

    if st.form_submit_button("🚀 送出電子簽核申請", type="primary", use_container_width=True):
        if leave_reason.strip():
            # 將資料寫入 session_state 的簽核資料庫
            if "approval_requests" not in st.session_state:
                st.session_state.approval_requests = []
            
            st.session_state.approval_requests.insert(0, {
                "單號": request_no,
                "類型": "請假申請",
                "申請人": st.session_state.get('user_name', 'admin'),
                "部門": "工程與設計管理中心",
                "內容": f"類別: {leave_type} | 時數: {leave_hours} 小時",
                "事由": leave_reason,
                "狀態": "🟡 待主管審核"
            })
            st.success(f"✅ 成功提交請假申請！時數共計：{leave_hours} 小時（含半小時精確計算），已送交主管審核。")
            st.rerun()
        else:
            st.warning("⚠️ 請完整填寫請假事由說明！")
