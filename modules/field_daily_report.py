import streamlit as st
import pandas as pd

def render_field_daily_report(engine=None, t=None, lang="繁體中文", **kwargs):
    # 多語言字典
    texts = {
        "繁體中文": {
            "title": "📋 現場工程日報表與出工統計管理",
            "info": "在此填報與管理每日工程進度、出工人數、現場耗料與施工日誌（支援案場資料隔離與預算連動）。",
            "search": "🔍 搜尋案場 / 日報編號 / 施工部位",
            "search_ph": "輸入關鍵字搜尋日報...",
            "list_title": "### 📋 歷史工程日報表總覽",
            "tab_add": "➕ 填寫新日報",
            "tab_edit": "✏️ 修改日報資料",
            "tab_del": "🗑️ 刪除日報",
            "step1": "📌 步驟 1: 選擇工程案場與填報日期",
            "project_label": "選擇工程案場 (Project / Site) *",
            "date_label": "填報日期 (Report Date) *",
            "weather_label": "當日天氣狀況 (Weather)",
            "step2": "📌 步驟 2: 當日出工人數統計 (Labor Attendance)",
            "tw_workers": "台籍師傅/工程師人數 (Taiwanese Staff)",
            "vn_workers": "越南籍技術員/技工人數 (Vietnamese Technicians)",
            "sub_workers": "外包/點工工人人數 (Subcontractors / Daily Workers)",
            "step3": "📌 步驟 3: 施工部位、進度與當日耗料記錄",
            "location_label": "當日施工部位 / 樓層 (Location / Zone) *",
            "desc_label": "當日施工內容與進度說明 (Work Description) *",
            "material_label": "當日耗用主要材料與數量 (Materials Used)",
            "add_btn": "🚀 提交並儲存工程日報表",
            "edit_title": "### ✏️ 修改工程日報表",
            "del_title": "### 🗑️ 刪除工程日報確認",
            "del_warn": "確定要刪除案場 **{site}** 在 **{date}** 的工程日報表嗎？",
            "del_btn": "🔥 確認刪除",
            "save_btn": "💾 儲存修改"
        },
        "Tiếng Việt": {
            "title": "📋 Nhật ký Thi công Công trình & Thống kê Nhân công",
            "info": "Quản lý và lập báo cáo tiến độ hàng ngày, số lượng nhân công, vật liệu tiêu hao tại công trường.",
            "search": "🔍 Tìm kiếm nhật ký thi công...",
            "search_ph": "Nhập từ khóa...",
            "list_title": "### 📋 Tổng quan Nhật ký Thi công",
            "tab_add": "➕ Thêm Nhật ký",
            "tab_edit": "✏️ Sửa Nhật ký",
            "tab_del": "🗑️ Xóa Nhật ký",
            "step1": "📌 Bước 1: Chọn Công trình & Ngày báo cáo",
            "project_label": "Chọn Công trình (Project / Site) *",
            "date_label": "Ngày báo cáo *",
            "weather_label": "Thời tiết hôm nay",
            "step2": "📌 Bước 2: Thống kê Số lượng Nhân công (Labor Attendance)",
            "tw_workers": "Số lượng thợ Đài Loan",
            "vn_workers": "Số lượng kỹ thuật viên Việt Nam",
            "sub_workers": "Số lượng công nhân thầu phụ / điểm công",
            "step3": "📌 Bước 3: Khu vực thi công, Tiến độ & Vật liệu tiêu hao",
            "location_label": "Khu vực / Tầng thi công *",
            "desc_label": "Mô tả công việc & Tiến độ *",
            "material_label": "Vật liệu tiêu hao & Số lượng",
            "add_btn": "🚀 Gửi & Lưu Nhật ký thi công",
            "edit_title": "### ✏️ Chỉnh sửa Nhật ký thi công",
            "del_title": "### 🗑️ Xác nhận xóa Nhật ký",
            "del_warn": "Bạn có chắc chắn muốn xóa nhật ký của công trình **{site}** ngày **{date}** không?",
            "del_btn": "🔥 Xác nhận xóa",
            "save_btn": "💾 Lưu thay đổi"
        },
        "English": {
            "title": "📋 Daily Construction Report & Labor Stats",
            "info": "Manage daily work progress, labor attendance, material consumption, and site logs.",
            "search": "🔍 Search Daily Reports...",
            "search_ph": "Enter keyword...",
            "list_title": "### 📋 Daily Construction Report Directory",
            "tab_add": "➕ Add Daily Report",
            "tab_edit": "✏️ Edit Daily Report",
            "tab_del": "🗑️ Delete Daily Report",
            "step1": "📌 Step 1: Select Project Site & Report Date",
            "project_label": "Project Site *",
            "date_label": "Report Date *",
            "weather_label": "Weather Condition",
            "step2": "📌 Step 2: Labor Attendance Statistics",
            "tw_workers": "Taiwanese Technicians Count",
            "vn_workers": "Vietnamese Technicians Count",
            "sub_workers": "Subcontractors / Daily Workers Count",
            "step3": "📌 Step 3: Work Location, Progress & Materials Used",
            "location_label": "Work Location / Zone *",
            "desc_label": "Work Description & Progress *",
            "material_label": "Materials Consumed & Quantity",
            "add_btn": "🚀 Submit & Save Daily Report",
            "edit_title": "### ✏️ Edit Daily Construction Report",
            "del_title": "### 🗑️ Confirm Report Deletion",
            "del_warn": "Are you sure you want to delete the report for **{site}** on **{date}**?",
            "del_btn": "🔥 Confirm Delete",
            "save_btn": "💾 Save Changes"
        }
    }

    t_set = texts.get(lang, texts["繁體中文"])

    st.title(t_set["title"])
    st.info(t_set["info"])

    # 初始化 Session State 模擬資料庫
    if "daily_report_db" not in st.session_state:
        st.session_state.daily_report_db = [
            {
                "日報編號": "DR-2026-001", "案場名稱": "西寧廠擴建工程 (Tay Ninh)", "填報日期": "2026-10-07", "天氣": "晴天 / Nắng",
                "台籍師傅人數": 2, "越籍技工人數": 12, "外包點工人數": 5, "總出工人數": 19,
                "施工部位": "A棟 1F 配電盤主干線配管", "施工內容": "完成 3 迴路 PVC 管路配置與穿線作業。", "耗用材料": "PVC管 2吋 30支, 4C×10mm² 電纜 150m", "填報人": "admin"
            }
        ]

    if "factory_list" not in st.session_state:
        st.session_state.factory_list = [
            {"廠區編號": "FAC-01", "廠區名稱": "西寧廠 (Tay Ninh)"},
            {"廠區編號": "FAC-02", "廠區名稱": "海防廠 (Hai Phong)"}
        ]

    # 搜尋與過濾
    search_q = st.text_input(t_set["search"], placeholder=t_set["search_ph"], key="report_search_input")
    filtered_reports = [
        r for r in st.session_state.daily_report_db 
        if search_q.lower() in r["案場名稱"].lower() or search_q.lower() in r["施工部位"].lower() or search_q.lower() in r["日報編號"].lower()
    ] if search_q else st.session_state.daily_report_db

    st.markdown(t_set["list_title"])
    st.dataframe(pd.DataFrame(filtered_reports), use_container_width=True)

    tab_add, tab_edit, tab_del = st.tabs([t_set["tab_add"], t_set["tab_edit"], t_set["tab_del"]])

    with tab_add:
        with st.form("add_daily_report_form"):
            st.markdown(f"### {t_set['step1']}")
            c1, c2, c3 = st.columns(3)
            with c1:
                site_choices = [f['廠區名稱'] for f in st.session_state.factory_list] if st.session_state.factory_list else ["西寧廠 (Tay Ninh)"]
                report_site = st.selectbox(t_set["project_label"], site_choices, key="report_site")
            with c2:
                report_date = st.date_input(t_set["date_label"], key="report_date")
            with c3:
                report_weather = st.selectbox(t_set["weather_label"], ["☀️ 晴天 (Sunny)", "⛅ 多雲 (Cloudy)", "🌧️ 雨天 (Rainy)"], key="report_weather")

            st.markdown("---")
            st.markdown(f"### {t_set['step2']}")
            l1, l2, l3 = st.columns(3)
            with l1:
                tw_count = st.number_input(t_set["tw_workers"], min_value=0, value=2, step=1, key="report_tw")
            with l2:
                vn_count = st.number_input(t_set["vn_workers"], min_value=0, value=10, step=1, key="report_vn")
            with l3:
                sub_count = st.number_input(t_set["sub_workers"], min_value=0, value=3, step=1, key="report_sub")
            
            total_workers = tw_count + vn_count + sub_count
            st.caption(f"👥 當日總出工人數 (Total Attendance): **{total_workers} 人**")

            st.markdown("---")
            st.markdown(f"### {t_set['step3']}")
            report_location = st.text_input(t_set["location_label"], placeholder="例如: 廠區 A棟 2樓機房", key="report_location")
            report_desc = st.text_area(t_set["desc_label"], placeholder="請詳述今日施工項目、進度百分比與現場狀況...", key="report_desc")
            report_material = st.text_input(t_set["material_label"], placeholder="例如: PVC管 2吋 20支, 镀鋅钢管 4吋 5支", key="report_material")

            st.markdown("---")
            if st.form_submit_button(t_set["add_btn"], type="primary"):
                if report_location and report_desc:
                    new_id = f"DR-2026-{len(st.session_state.daily_report_db)+1:03d}"
                    st.session_state.daily_report_db.append({
                        "日報編號": new_id,
                        "案場名稱": report_site,
                        "填報日期": str(report_date),
                        "天氣": report_weather,
                        "台籍師傅人數": tw_count,
                        "越籍技工人數": vn_count,
                        "外包點工人數": sub_count,
                        "總出工人數": total_workers,
                        "施工部位": report_location,
                        "施工內容": report_desc,
                        "耗用材料": report_material,
                        "填報人": st.session_state.get("user_name", "admin")
                    })
                    success_msg = "Thêm nhật ký thành công!" if lang == "Tiếng Việt" else ("Daily report added successfully!" if lang == "English" else f"✅ 工程日報表 {new_id} 提交並儲存成功！")
                    st.success(success_msg)
                    st.rerun()
                else:
                    warn_msg = "Vui lòng nhập đầy đủ khu vực và nội dung!" if lang == "Tiếng Việt" else ("Please enter work location and description!" if lang == "English" else "⚠️ 請填寫施工部位與施工內容說明！")
                    st.warning(warn_msg)

    with tab_edit:
        if st.session_state.daily_report_db:
            rep_opts = {f"{r['日報編號']} - {r['案場名稱']} ({r['填報日期']})": r for r in st.session_state.daily_report_db}
            sel_rep_key = st.selectbox("選擇要修改的日報", list(rep_opts.keys()), key="edit_rep_select")
            target_rep = rep_opts[sel_rep_key]

            with st.form("edit_daily_report_form"):
                st.markdown(t_set["edit_title"])
                ed_loc = st.text_input("施工部位", value=target_rep["施工部位"], key="edit_ed_loc")
                ed_desc = st.text_area("施工內容說明", value=target_rep["施工內容"], key="edit_ed_desc")
                ed_mat = st.text_input("耗用材料", value=target_rep["耗用材料"], key="edit_ed_mat")
                ed_tw = st.number_input("台籍師傅人數", min_value=0, value=int(target_rep["台籍師傅人數"]), key="edit_ed_tw")
                ed_vn = st.number_input("越籍技工人數", min_value=0, value=int(target_rep["越籍技工人數"]), key="edit_ed_vn")
                ed_sub = st.number_input("外包點工人數", min_value=0, value=int(target_rep["外包點工人數"]), key="edit_ed_sub")

                if st.form_submit_button(t_set["save_btn"], type="primary"):
                    for r in st.session_state.daily_report_db:
                        if r["日報編號"] == target_rep["日報編號"]:
                            r["施工部位"] = ed_loc
                            r["施工內容"] = ed_desc
                            r["耗用材料"] = ed_mat
                            r["台籍師傅人數"] = ed_tw
                            r["越籍技工人數"] = ed_vn
                            r["外包點工人數"] = ed_sub
                            r["總出工人數"] = ed_tw + ed_vn + ed_sub
                    st.success("✅ 日報表更新成功！")
                    st.rerun()
        else:
            st.info("目前無日報資料可供修改。")

    with tab_del:
        if st.session_state.daily_report_db:
            del_opts = {f"{r['日報編號']} - {r['案場名稱']} ({r['填報日期']})": r for r in st.session_state.daily_report_db}
            sel_del_key = st.selectbox("選擇要刪除的日報", list(del_opts.keys()), key="del_rep_select")
            target_del = del_opts[sel_del_key]

            with st.form("delete_daily_report_form"):
                st.markdown(t_set["del_title"])
                st.warning(t_set["del_warn"].format(site=target_del['案場名稱'], date=target_del['填報日期']))
                if st.form_submit_button(t_set["del_btn"], type="primary"):
                    st.session_state.daily_report_db = [r for r in st.session_state.daily_report_db if r["日報編號"] != target_del["日報編號"]]
                    st.success("✅ 日報表已成功刪除！")
                    st.rerun()
        else:
            st.info("目前無日報資料可供刪除。")

def show(*args, **kwargs):
    render_field_daily_report(*args, **kwargs)

def main(*args, **kwargs):
    render_field_daily_report(*args, **kwargs)
