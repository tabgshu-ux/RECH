import streamlit as st
import pandas as pd
from sqlalchemy import text

def render(engine=None, lang="繁體中文", **kwargs):
    # 🌍 支援多語系的介面文字字典
    UI_TEXTS = {
        "繁體中文": {
            "title": "🏢 智慧企業部門與自動模組拼圖管理",
            "caption": "SaaS 架構核心：系統根據部門性質自動掛載對應模組，免除手動勾選工程代碼的繁瑣操作。",
            "tenant_label": "📍 目前作用中企業租戶 (Tenant ID)：",
            "table_header": "📋 現有部門與自動掛載功能對照表",
            "add_header": "➕ 動態新增企業部門（系統將自動智慧配屬對應功能）",
            "dept_name_label": "新部門名稱 (例如: 永續發展辦公室 / Phòng Phát triển Bền vững)",
            "dept_type_label": "選擇部門業務性質 (自動掛載對應模組)",
            "sort_label": "排序編號 (Sort Order)",
            "save_btn": "💾 儲存並自動建立部門元數據",
            "success_msg": "🎉 成功新增部門，系統已自動依據性質掛載對應模組！"
        },
        "Tiếng Việt": {
            "title": "🏢 Quản lý Phòng ban & Tự động Gắn kết Module",
            "caption": "Core SaaS: Hệ thống tự động gắn kết các module tương ứng dựa trên tính chất phòng ban, loại bỏ việc chọn mã code phức tạp.",
            "tenant_label": "📍 Doanh nghiệp hiện tại (Tenant ID):",
            "table_header": "📋 Bảng đối chiếu phòng ban & tính năng tự động",
            "add_header": "➕ Thêm phòng ban mới (Hệ thống tự động cấu hình module)",
            "dept_name_label": "Tên phòng ban mới (Ví dụ: Phòng Phát triển Bền vững)",
            "dept_type_label": "Chọn tính chất nghiệp vụ (Tự động gắn module)",
            "sort_label": "Thứ tự sắp xếp (Sort Order)",
            "save_btn": "💾 Lưu và tự động tạo metadata",
            "success_msg": "🎉 Thêm phòng ban thành công, hệ thống đã tự động gán module tương ứng!"
        },
        "English": {
            "title": "🏢 Smart Department & Auto-Module Configuration",
            "caption": "SaaS Core: Automatically bind corresponding modules based on department nature, avoiding manual code selection.",
            "tenant_label": "📍 Current Tenant ID:",
            "table_header": "📋 Department & Auto-Assigned Modules Table",
            "add_header": "➕ Add New Department (Auto-binds appropriate features)",
            "dept_name_label": "New Department Name (e.g., Sustainability Office)",
            "dept_type_label": "Select Department Type (Auto-configures modules)",
            "sort_label": "Sort Order",
            "save_btn": "💾 Save & Auto-Configure Metadata",
            "success_msg": "🎉 Successfully added department with auto-configured modules!"
        }
    }

    t = UI_TEXTS.get(lang, UI_TEXTS["繁體中文"])

    st.markdown(f"### {t['title']}")
    st.caption(t['caption'])

    if not engine:
        st.warning("⚠️ 系統尚未連線至資料庫引擎 (`engine`)，目前為離線展示模式。")
        return

    current_tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    st.info(f"{t['tenant_label']} **{current_tenant_id}**")

    # 🏢 預定義的產業與部門業務性質對應表（具備越、中、英直覺描述，再也不用看英文代碼）
    DEPARTMENT_PRESETS = {
        "總經理室 (Executive Office / Ban Tổng Giám đốc)": {
            "modules": ["commodities_fx", "financials_pl", "project_progress", "vietnam_policy"],
            "desc_vi": "Chiến lược, Tài chính, LME, Chính sách VN"
        },
        "管理部 (Management Dept / Phòng Hành chính - Nhân sự)": {
            "modules": ["announcements", "hr_records", "accounting_ap_ar"],
            "desc_vi": "Nhân sự, Ký túc xá, Xe cộ, Kế toán - Thuế"
        },
        "工程與設計管理中心 (Engineering Center / Trung tâm Kỹ thuật)": {
            "modules": ["eng_dashboard", "quotation", "daily_report", "fat_sat"],
            "desc_vi": "Báo giá, Nhật ký thi công, Bản vẽ tủ điện, FAT/SAT"
        },
        "生產部 (Production Dept / Bộ phận Sản xuất)": {
            "modules": ["sheet_metal", "painting", "assembly"],
            "desc_vi": "Gia công Chấn dập, Sơn tĩnh điện, Lắp ráp tủ điện"
        },
        "倉庫管理 (Warehouse / Quản lý Kho)": {
            "modules": ["inventory_barcodes"],
            "desc_vi": "Quản lý tồn kho, Mã vạch vật tư"
        },
        "外勤打卡與回報 (Field Attendance / Chấm công hiện trường)": {
            "modules": ["field_gps_attendance"],
            "desc_vi": "Chấm công GPS, Báo cáo công việc hiện trường"
        },
        "電子簽核中心 (Approval Center / Trung tâm Phê duyệt)": {
            "modules": ["approval_workflow"],
            "desc_vi": "Quy trình phê duyệt đơn từ, Mua sắm, Nghỉ phép"
        }
    }

    # 讀取現有部門
    try:
        with engine.connect() as conn:
            query = text("SELECT dept_id, dept_name, sort_order, assigned_modules, is_active FROM tenant_departments WHERE tenant_id = :tid ORDER BY sort_order ASC")
            df_depts = pd.read_sql(query, con=conn, params={"tid": current_tenant_id})
    except Exception:
        df_depts = pd.DataFrame([
            {"dept_id": "D01", "dept_name": "📈 總经理室 (Ban Tổng Giám đốc)", "sort_order": 1, "assigned_modules": "即時戰情與 Thông tư 200 財報", "is_active": True},
            {"dept_id": "D02", "dept_name": "👔 管理部 (Phòng Hành chính - Nhân sự)", "sort_order": 2, "assigned_modules": "人事、總務、財會管理", "is_active": True},
            {"dept_id": "D03", "dept_name": "🛠️ 工程與設計管理中心 (Trung tâm Kỹ thuật)", "sort_order": 3, "assigned_modules": "專案報價、施工日報、FAT/SAT", "is_active": True},
            {"dept_id": "D04", "dept_name": "🏭 生產部 (Bộ phận Sản xuất)", "sort_order": 4, "assigned_modules": "板金、塗料、配盤組裝", "is_active": True},
            {"dept_id": "D05", "dept_name": "📦 倉庫管理 (Quản lý Kho)", "sort_order": 5, "assigned_modules": "資材與條碼倉管", "is_active": True},
            {"dept_id": "D06", "dept_name": "📍 外勤工程打卡 (Chấm công hiện trường)", "sort_order": 6, "assigned_modules": "GPS 外勤打卡與工作回報", "is_active": True},
            {"dept_id": "D07", "dept_name": "✍️ 電子簽核中心 (Trung tâm Phê duyệt)", "sort_order": 7, "assigned_modules": "多級電子簽核", "is_active": True},
        ])

    st.markdown(f"#### {t['table_header']}")
    st.dataframe(df_depts, use_container_width=True)

    st.markdown("---")
    st.markdown(f"#### {t['add_header']}")
    
    with st.form("auto_dept_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_dept_name = st.text_input(t['dept_name_label'])
            new_sort_order = st.number_input(t['sort_label'], min_value=1, max_value=99, value=8)
        with col2:
            selected_preset_key = st.selectbox(t['dept_type_label'], list(DEPARTMENT_PRESETS.keys()))
            preset_info = DEPARTMENT_PRESETS[selected_preset_key]
            st.info(f"🇻🇳 **越南語對應說明 (Tiếng Việt)**：{preset_info['desc_vi']}")

        submitted = st.form_submit_button(t['save_btn'])
        if submitted:
            if new_dept_name:
                auto_modules_str = ", ".join(preset_info["modules"])
                try:
                    with engine.begin() as conn:
                        insert_sql = text("""
                            INSERT INTO tenant_departments (tenant_id, dept_name, sort_order, assigned_modules, is_active)
                            VALUES (:tid, :dname, :sort, :mods, :act)
                        """)
                        conn.execute(insert_sql, {
                            "tid": current_tenant_id,
                            "dname": new_dept_name,
                            "sort": new_sort_order,
                            "mods": auto_modules_str,
                            "act": True
                        })
                    st.success(t['success_msg'])
                    st.rerun()
                except Exception as db_err:
                    st.error(f"⚠️ 寫入資料庫失敗：{str(db_err)}")
            else:
                st.error("⚠️ 請輸入有效的部門名稱！")
