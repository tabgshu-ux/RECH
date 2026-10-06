import datetime
import io
import pandas as pd
from sqlalchemy import text
import streamlit as st

# ----------------------------------------------------
# 🌐 應收帳款與專案進度模組多語系字典 (i18n)
# ----------------------------------------------------
AR_I18N = {
    "繁體中文": {
        "title": "📜 資訊與管理中心 - 客戶應收帳款 (AR) 與專案進度",
        "caption": "管理總合約金額、分期付款進度與催收記錄。",
        "tab_list": "📊 應收帳款與進度清冊",
        "tab_update": "✏️ 更新進度 & 催收款項理由",
        "tab_add": "➕ 登記新應收帳款專案",
        "table_title": "📊 客戶應收帳款專案清冊",
        "search_label": "搜尋合約 / 客戶 / 專案：",
        "update_title": "🔧 修改專案進行進度說明與催收紀錄",
        "select_project_update": "請選擇要更新進度的款款專案：",
        "current_project": "當前專案",
        "update_progress_label": "更新「進行進度說明」*",
        "update_reminder_label": "更新/追加「催收款項與客戶回應」",
        "modifier_name": "修改人員姓名*",
        "save_update_btn": "💾 儲存並更新專案進度",
        "add_title": "➕ 登記新應收帳款專案",
        "ar_code": "款項編號*",
        "payment_mode": "付款期數模式*",
        "client_name": "客戶名稱*",
        "project_desc": "專案說明",
        "project_name": "工程名稱*",
        "currency": "交易幣別*",
        "progress_desc": "進行進度說明",
        "total_amount": "總帳款*",
        "milestone_title": "📅 分期百分比 (%) 與付款日期細項設定",
        "payment_date": "付款日期",
        "save_new_btn": "💾 儲存並登記新專案",
        "success_update": "✅ 專案進度與催收紀錄已成功更新！",
        "success_add": "✅ 新應收帳款專案已成功登記！"
    },
    "Tiếng Việt": {
        "title": "📜 Khối Quản lý - Phải thu Khách hàng (AR) & Tiến độ Dự án",
        "caption": "Quản lý tổng số tiền hợp đồng, lịch trình thanh toán theo đợt, cập nhật tiến độ.",
        "tab_list": "📊 Danh sách Phải thu & Tiến độ",
        "tab_update": "✏️ Cập nhật Tiến độ & Lý do thu nợ",
        "tab_add": "➕ Thêm Dự án Phải thu Mới",
        "table_title": "📊 Sổ chi tiết Phải thu Khách hàng",
        "search_label": "Tìm kiếm hợp đồng / khách hàng / dự án:",
        "update_title": "📌 Sửa đổi tiến độ dự án và ghi chú thu nợ",
        "select_project_update": "Chọn dự án cần cập nhật tiến độ:",
        "current_project": "Dự án hiện tại",
        "update_progress_label": "Cập nhật \"Mô tả tiến độ\" *",
        "update_reminder_label": "Cập nhật/Bổ sung \"Lý do thu nợ & phản hồi từ khách hàng\"",
        "modifier_name": "Họ tên người sửa*",
        "save_update_btn": "💾 Lưu và cập nhật tiến độ dự án",
        "add_title": "➕ Đăng ký dự án khoản phải thu mới",
        "ar_code": "Mã khoản thu*",
        "payment_mode": "Hình thức thanh toán*",
        "client_name": "Tên khách hàng*",
        "project_desc": "Mô tả dự án",
        "project_name": "Tên công trình*",
        "currency": "Loại tiền tệ*",
        "progress_desc": "Mô tả tiến độ",
        "total_amount": "Tổng khoản nợ*",
        "milestone_title": "📅 Thiết lập chi tiết tỷ lệ phần trăm (%) và ngày thanh toán",
        "payment_date": "Ngày thanh toán",
        "save_new_btn": "💾 Lưu và đăng ký dự án mới",
        "success_update": "✅ Đã cập nhật thành công tiến độ và ghi chú thu nợ!",
        "success_add": "✅ Đã đăng ký thành công dự án khoản phải thu mới!"
    },
    "English": {
        "title": "📜 Management Dept - Accounts Receivable (AR) & Project Progress",
        "caption": "Manage total contract amounts, installment schedules, and collection records.",
        "tab_list": "📊 AR & Progress Summary",
        "tab_update": "✏️ Update Progress & Collection Remarks",
        "tab_add": "➕ Register New AR Project",
        "table_title": "📊 Customer Accounts Receivable Registry",
        "search_label": "Search contract / client / project:",
        "update_title": "🔧 Modify Project Progress & Collection Log",
        "select_project_update": "Select project to update:",
        "current_project": "Current Project",
        "update_progress_label": "Update Progress Description *",
        "update_reminder_label": "Update/Append Collection Remarks & Client Feedback",
        "modifier_name": "Modifier Name *",
        "save_update_btn": "💾 Save & Update Project Progress",
        "add_title": "➕ Register New Accounts Receivable Project",
        "ar_code": "AR Code *",
        "payment_mode": "Payment Terms *",
        "client_name": "Client Name *",
        "project_desc": "Project Description",
        "project_name": "Project / Engineering Name *",
        "currency": "Currency *",
        "progress_desc": "Progress Description",
        "total_amount": "Total Amount *",
        "milestone_title": "📅 Milestone Installment Percentage (%) & Due Dates",
        "payment_date": "Payment Date",
        "save_new_btn": "💾 Save & Register New Project",
        "success_update": "✅ Project progress and collection records successfully updated!",
        "success_add": "✅ New AR project successfully registered!"
    }
}

def get_ar_lang_dict(lang_param):
    active_lang = lang_param or st.session_state.get("lang", "繁體中文")
    return AR_I18N.get(active_lang, AR_I18N["繁體中文"])

def render_ar_management_page(engine=None, lang="繁體中文"):
    active_lang = lang or st.session_state.get("lang", "繁體中文")
    L = get_ar_lang_dict(active_lang)

    st.title(L["title"])
    st.caption(L["caption"])

    tab_list, tab_update, tab_add = st.tabs([
        L["tab_list"],
        L["tab_update"],
        L["tab_add"]
    ])

    # 模擬或讀取資料庫中的 AR 專案
    if "ar_projects_db" not in st.session_state:
        st.session_state.ar_projects_db = [
            {
                "code": "INV-2026-001",
                "client": "越南樟榜工業區A廠",
                "project": "西寧廠 2000A 配電櫃新建工程",
                "currency": "USD",
                "total": 50000.0,
                "mode": "不分期",
                "progress": "工程備料中 / 準備施工",
                "desc": "合約包含高低壓配電盤安裝及試車",
                "reminder": "【2026-10-02 03:37 催款員: admin】客戶延至 2026-10-17 付款。理由：說工程未驗收完成，等驗收完成才付款"
            }
        ]

    # ----------------------------------------------------
    # 📊 頁籤一：應收帳款與進度清冊
    # ----------------------------------------------------
    with tab_list:
        st.markdown(f"### {L['table_title']}")
        search_query = st.text_input(L["search_label"], key="ar_search_input")
        
        df_ar = pd.DataFrame(st.session_state.ar_projects_db)
        if search_query:
            df_ar = df_ar[df_ar.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

        st.dataframe(df_ar, use_container_width=True)

    # ----------------------------------------------------
    # ✏️ 頁籤二：更新進度 & 催收款項理由
    # ----------------------------------------------------
    with tab_update:
        st.markdown(f"### {L['update_title']}")
        
        if not st.session_state.ar_projects_db:
            st.info("尚無應收帳款專案可供更新。")
        else:
            proj_opts = {f"{p['code']} - {p['client']} ({p['project']})": p for p in st.session_state.ar_projects_db}
            selected_proj_label = st.selectbox(L["select_project_update"], list(proj_opts.keys()), key="sel_ar_proj")
            selected_proj = proj_opts[selected_proj_label]

            st.info(f"{L['current_project']}: **{selected_proj['code']}** | 總帳款: `{selected_proj['total']:,.3f} {selected_proj['currency']}`")

            with st.form(key="update_ar_form"):
                new_progress = st.text_area(L["update_progress_label"], value=selected_proj.get("progress", ""))
                new_reminder = st.text_area(L["update_reminder_label"], value=selected_proj.get("reminder", ""))
                modifier = st.text_input(L["modifier_name"], value="admin")

                submitted = st.form_submit_button(L["save_update_btn"], type="primary")
                if submitted:
                    selected_proj["progress"] = new_progress
                    selected_proj["reminder"] = new_reminder
                    st.success(L["success_update"])

    # ----------------------------------------------------
    # ➕ 頁籤三：登記新應收帳款專案
    # ----------------------------------------------------
    with tab_add:
        st.markdown(f"### {L['add_title']}")

        with st.form(key="add_ar_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_code = st.text_input(L["ar_code"], value=f"AR-2026-{datetime.datetime.now().strftime('%H%M%S')}")
                client_name = st.text_input(L["client_name"], value="越南樟榜工業區A廠")
                project_name = st.text_input(L["project_name"], value="西寧廠 2000A 配電櫃新建工程")
                currency = st.selectbox(L["currency"], ["VND", "USD", "TWD", "CNY"])
                total_amt = st.number_input(L["total_amount"], value=100000.0, step=10000.0)
            with c2:
                payment_mode = st.selectbox(L["payment_mode"], ["不分期", "分三期 (30%, 30%, 40%)", "按月計價工程款"])
                project_desc = st.text_area(L["project_desc"], value="請填寫工程施工內容與合約細節...")
                progress_desc = st.text_area(L["progress_desc"], value="工程備料中 / 準備施工")

            st.markdown(f"#### {L['milestone_title']}")
            st.date_input(L["payment_date"], value=datetime.date.today(), key="pay_date_input")

            submitted_add = st.form_submit_button(L["save_new_btn"], type="primary")
            if submitted_add:
                new_item = {
                    "code": new_code,
                    "client": client_name,
                    "project": project_name,
                    "currency": currency,
                    "total": total_amt,
                    "mode": payment_mode,
                    "progress": progress_desc,
                    "desc": project_desc,
                    "reminder": f"【{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} 建立專案】"
                }
                st.session_state.ar_projects_db.append(new_item)
                st.success(L["success_add"])

def show(engine=None, lang="繁體中文"):
    render_ar_management_page(engine, lang)

def main(engine=None, lang="繁體中文"):
    render_ar_management_page(engine, lang)
