import streamlit as st
import pandas as pd
import datetime

# ----------------------------------------------------
# 🌐 採購與應付帳款 (AP) 模組多語系字典 (i18n)
# ----------------------------------------------------
PURCHASING_AP_I18N = {
    "繁體中文": {
        "title": "🛒 財務部 - 採購管理與應付帳款 (AP) 及供應商分類系統",
        "caption": "管理土地租賃合約、公司用車、生產原料、固定資產與各類供應商分類清冊與應付帳款追蹤。",
        "tab_vendor": "🤝 供應商分類與名冊管理",
        "tab_ap_list": "📑 應付帳款 (AP) 總表與進度追蹤",
        "tab_ap_add": "➕ 登記新採購與應付帳款 (AP)",
        "tab_ap_update": "🔄 更新 AP 付款狀態",
        "vendor_header": "📋 依採購種類區分之供應商名冊 (Supplier Directory by Category)",
        "ap_header": "📋 廠區應付帳款 (AP) 與款項支付進度總表",
        "cat_opts": [
            "🏭 原物料與加工零件供應商 (Raw Materials & Parts)",
            "🏢 土地與廠房房東 / 物業 (Landlord & Facilities)",
            "🚚 運輸物流與車輛維修 (Logistics & Vehicles)",
            "⚡ 水電能源與政府規費 (Utilities & Gov Fees)",
            "💻 IT 設備與辦公耗材 (IT & Office Supplies)"
        ],
        "lbl_v_code": "供應商編號 *",
        "lbl_v_name": "供應商名稱 / 公司行號 *",
        "lbl_v_cat": "採購與供應種類 *",
        "lbl_v_contact": "主要聯絡人與電話",
        "lbl_v_tax": "稅號 (Mã số thuế / Tax Code)",
        "btn_add_vendor": "🚀 新增供應商至分類資料庫",
        "success_add_vendor": "✅ 成功新增供應商 `{name}`！",
        "lbl_ap_no": "AP / 採購單號 *",
        "lbl_ap_vendor": "選擇供應商 *",
        "lbl_ap_desc": "採購項目與說明 *",
        "lbl_ap_amount": "應付金額 (USD 或 VND) *",
        "lbl_ap_duedate": "款項到期日 *",
        "lbl_ap_status": "付款狀態 *",
        "status_opts": ["🟡 未付款 (Unpaid)", "🔵 部分付款 (Partial)", "🟢 已付清 (Paid)"],
        "btn_add_ap": "💾 儲存應付帳款 (AP) 紀錄",
        "success_add_ap": "✅ AP 單號 `{no}` 已成功建立！",
        "col_v_index": "STT",
        "col_v_code": "供應商編號",
        "col_v_name": "供應商名稱",
        "col_v_cat": "供應種類",
        "col_v_contact": "聯絡資訊",
        "col_v_tax": "稅號",
        "col_ap_index": "STT",
        "col_ap_no": "AP單號",
        "col_ap_vendor": "供應商",
        "col_ap_desc": "採購說明",
        "col_ap_amount": "金額",
        "col_ap_date": "到期日",
        "col_ap_status": "付款狀態"
    },
    "Tiếng Việt": {
        "title": "🛒 Quản lý Mua hàng, Công nợ Phải trả (AP) & Nhà cung cấp",
        "caption": "Quản lý danh mục nhà cung cấp theo ngành hàng và theo dõi công nợ AP.",
        "tab_vendor": "🤝 Quản lý Danh mục Nhà cung cấp",
        "tab_ap_list": "📑 Danh sách AP & Tiến độ thanh toán",
        "tab_ap_add": "➕ Thêm Khoản phải trả (AP)",
        "tab_ap_update": "🔄 Cập nhật Trạng thái AP",
        "vendor_header": "📋 Danh sách Nhà cung cấp theo phân loại",
        "ap_header": "📋 Bảng tổng hợp công nợ phải trả AP",
        "cat_opts": [
            "🏭 原物料與加工零件供應商 (Raw Materials & Parts)",
            "🏢 土地與廠房房東 / 物業 (Landlord & Facilities)",
            "🚚 運輸物流與車輛維修 (Logistics & Vehicles)",
            "⚡ 水電能源與政府規費 (Utilities & Gov Fees)",
            "💻 IT 設備與辦公耗材 (IT & Office Supplies)"
        ],
        "lbl_v_code": "Mã NCC *",
        "lbl_v_name": "Tên Nhà cung cấp *",
        "lbl_v_cat": "Phân loại mua hàng *",
        "lbl_v_contact": "Người liên hệ & SĐT",
        "lbl_v_tax": "Mã số thuế",
        "btn_add_vendor": "🚀 Thêm Nhà cung cấp",
        "success_add_vendor": "✅ Đã thêm NCC `{name}` thành công!",
        "lbl_ap_no": "Mã AP / Đơn hàng *",
        "lbl_ap_vendor": "Chọn Nhà cung cấp *",
        "lbl_ap_desc": "Nội dung mua hàng *",
        "lbl_ap_amount": "Số tiền *",
        "lbl_ap_duedate": "Ngày đến hạn *",
        "lbl_ap_status": "Trạng thái *",
        "status_opts": ["🟡 Chưa thanh toán", "🔵 Thanh toán một phần", "🟢 Đã thanh toán"],
        "btn_add_ap": "💾 Lưu khoản phải trả",
        "success_add_ap": "✅ Đã tạo mã AP `{no}` thành công!",
        "col_v_index": "STT",
        "col_v_code": "Mã NCC",
        "col_v_name": "Tên NCC",
        "col_v_cat": "Phân loại",
        "col_v_contact": "Liên hệ",
        "col_v_tax": "Mã số thuế",
        "col_ap_index": "STT",
        "col_ap_no": "Mã AP",
        "col_ap_vendor": "Nhà cung cấp",
        "col_ap_desc": "Nội dung",
        "col_ap_amount": "Số tiền",
        "col_ap_date": "Hạn thanh toán",
        "col_ap_status": "Trạng thái"
    },
    "English": {
        "title": "🛒 Purchasing, Accounts Payable (AP) & Supplier Management",
        "caption": "Manage suppliers categorized by purchased items and track AP lifecycle.",
        "tab_vendor": "🤝 Supplier Categories & Directory",
        "tab_ap_list": "📑 AP Directory & Payment Status",
        "tab_ap_add": "➕ Register AP Record",
        "tab_ap_update": "🔄 Update Payment Status",
        "vendor_header": "📋 Supplier Directory by Purchasing Category",
        "ap_header": "📋 Accounts Payable (AP) Master Log",
        "cat_opts": [
            "🏭 原物料與加工零件供應商 (Raw Materials & Parts)",
            "🏢 土地與廠房房東 / 物業 (Landlord & Facilities)",
            "🚚 運輸物流與車輛維修 (Logistics & Vehicles)",
            "⚡ 水電能源與政府規費 (Utilities & Gov Fees)",
            "💻 IT 設備與辦公耗材 (IT & Office Supplies)"
        ],
        "lbl_v_code": "Supplier Code *",
        "lbl_v_name": "Supplier Name *",
        "lbl_v_cat": "Purchasing Category *",
        "lbl_v_contact": "Contact Info",
        "lbl_v_tax": "Tax Code",
        "btn_add_vendor": "🚀 Add Supplier",
        "success_add_vendor": "✅ Successfully added supplier `{name}`!",
        "lbl_ap_no": "AP / Order No. *",
        "lbl_ap_vendor": "Select Supplier *",
        "lbl_ap_desc": "Description *",
        "lbl_ap_amount": "Amount *",
        "lbl_ap_duedate": "Due Date *",
        "lbl_ap_status": "Status *",
        "status_opts": ["🟡 Unpaid", "🔵 Partial", "🟢 Paid"],
        "btn_add_ap": "💾 Save AP Record",
        "success_add_ap": "✅ AP record `{no}` saved successfully!",
        "col_v_index": "No.",
        "col_v_code": "Code",
        "col_v_name": "Supplier Name",
        "col_v_cat": "Category",
        "col_v_contact": "Contact",
        "col_v_tax": "Tax Code",
        "col_ap_index": "No.",
        "col_ap_no": "AP No.",
        "col_ap_vendor": "Supplier",
        "col_ap_desc": "Description",
        "col_ap_amount": "Amount",
        "col_ap_date": "Due Date",
        "col_ap_status": "Status"
    }
}

def render_procurement_ap_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang or st.session_state.get("current_lang", "繁體中文")
    L = PURCHASING_AP_I18N.get(active_lang, PURCHASING_AP_I18N["繁體中文"])

    st.title(L["title"])
    st.caption(L["caption"])

    # 初始化供應商資料庫
    if "supplier_db" not in st.session_state:
        st.session_state.supplier_db = [
            {
                "供應商編號": "SUP-TN-001",
                "供應商名稱": "An Tinh Industrial Park Corp (西寧工業區房東)",
                "採購與供應種類": "🏢 土地與廠房房東 / 物業 (Landlord & Facilities)",
                "主要聯絡人與電話": "Mr. Nam (+84 901 234 567)",
                "稅號": "3901234567"
            },
            {
                "供應商編號": "SUP-MAT-001",
                "供應商名稱": "Thành Phát Copper & Steel Co., Ltd",
                "採購與供應種類": "🏭 原物料與加工零件供應商 (Raw Materials & Parts)",
                "主要聯絡人與電話": "Ms. Linh (+84 918 888 999)",
                "稅號": "3709876543"
            },
            {
                "供應商編號": "SUP-LOG-001",
                "供應商名稱": "Thaco Gò Dầu (車輛維修與保養廠)",
                "採購與供應種類": "🚚 運輸物流與車輛維修 (Logistics & Vehicles)",
                "主要聯絡人與電話": "Service Center (+84 274 3838 888)",
                "稅號": "3501112223"
            },
            {
                "供應商編號": "SUP-GOV-001",
                "供應商名稱": "Tay Ninh Electricity Power (EVN 西寧電力)",
                "採購與供應種類": "⚡ 水電能源與政府規費 (Utilities & Gov Fees)",
                "主要聯絡人與電話": "Hotline 1900 1000",
                "稅號": "3900011122"
            }
        ]

    # 初始化應付帳款 (AP) 資料庫
    if "ap_db" not in st.session_state:
        st.session_state.ap_db = [
            {
                "AP單號": "AP-2026-001",
                "供應商": "An Tinh Industrial Park Corp (西寧工業區房東)",
                "採購說明": "2026年度第二季西寧廠廠房與土地租金",
                "應付金額": 12000.0,
                "到期日": "2026-06-30",
                "付款狀態": "🟡 未付款 (Unpaid)"
            },
            {
                "AP單號": "AP-2026-002",
                "供應商": "Thành Phát Copper & Steel Co., Ltd",
                "採購說明": "生產銅排母線原物料採購一批",
                "應付金額": 24500.0,
                "到期日": "2026-04-15",
                "付款狀態": "🟢 已付清 (Paid)"
            }
        ]

    # 頂部分頁籤
    tab_vendor, tab_ap_list, tab_ap_add, tab_ap_update = st.tabs([
        L["tab_vendor"], L["tab_ap_list"], L["tab_ap_add"], L["tab_ap_update"]
    ])

    # 1. 🤝 供應商分類與名冊管理
    with tab_vendor:
        st.markdown(f"### {L['vendor_header']}")
        st.caption("您可以依採購種類檢視所有供應商，並可隨時新增或維護廠商資料與越南稅號。")

        all_cats = ["🌐 全部供應商 (All Categories)"] + L["cat_opts"]
        selected_v_cat_filter = st.selectbox("🔍 依採購與供應種類篩選 (Filter by Category)", all_cats)

        filtered_vendors = st.session_state.supplier_db
        if selected_v_cat_filter != "🌐 全部供應商 (All Categories)":
            filtered_vendors = [v for v in filtered_vendors if v["採購與供應種類"] == selected_v_cat_filter]

        if filtered_vendors:
            v_display = []
            for idx, v in enumerate(filtered_vendors, 1):
                v_display.append({
                    L["col_v_index"]: idx,
                    L["col_v_code"]: v.get("供應商編號", "-"),
                    L["col_v_name"]: v.get("供應商名稱", "-"),
                    L["col_v_cat"]: v.get("採購與供應種類", "-"),
                    L["col_v_contact"]: v.get("主要聯絡人與電話", "-"),
                    L["col_v_tax"]: v.get("稅號", "-")
                })
            st.dataframe(pd.DataFrame(v_display), use_container_width=True)
        else:
            st.info("目前此分類中尚無供應商記錄。")

        st.markdown("---")
        st.markdown("#### ➕ 登記新供應商（依種類歸類）")
        with st.form("form_add_vendor"):
            vc1, vc2 = st.columns(2)
            with vc1:
                auto_v_code = f"SUP-{len(st.session_state.supplier_db)+1:03d}"
                v_code = st.text_input(L["lbl_v_code"], value=auto_v_code)
                v_name = st.text_input(L["lbl_v_name"])
            with vc2:
                v_cat = st.selectbox(L["lbl_v_cat"], L["cat_opts"])
                v_tax = st.text_input(L["lbl_v_tax"], placeholder="例如: 3901234567")

            v_contact = st.text_input(L["lbl_v_contact"], placeholder="例如: Mr. Minh (+84 90... )")

            if st.form_submit_button(L["btn_add_vendor"], type="primary", use_container_width=True):
                if v_code and v_name:
                    st.session_state.supplier_db.append({
                        "供應商編號": v_code,
                        "供應商名稱": v_name,
                        "採購與供應種類": v_cat,
                        "主要聯絡人與電話": v_contact if v_contact else "-",
                        "稅號": v_tax if v_tax else "-"
                    })
                    st.success(L["success_add_vendor"].format(name=v_name))
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫供應商編號與名稱！")

    # 2. 📑 應付帳款 (AP) 總表與進度追蹤
    with tab_ap_list:
        st.markdown(f"### {L['ap_header']}")
        if st.session_state.ap_db:
            ap_display = []
            for idx, ap in enumerate(st.session_state.ap_db, 1):
                ap_display.append({
                    L["col_ap_index"]: idx,
                    L["col_ap_no"]: ap.get("AP單號", "-"),
                    L["col_ap_vendor"]: ap.get("供應商", "-"),
                    L["col_ap_desc"]: ap.get("採購說明", "-"),
                    L["col_ap_amount"]: f"${float(ap.get('應付金額', 0)):,.2f} USD",
                    L["col_ap_date"]: ap.get("到期日", "-"),
                    L["col_ap_status"]: ap.get("付款狀態", "-")
                })
            st.dataframe(pd.DataFrame(ap_display), use_container_width=True)
        else:
            st.info("目前無任何應付帳款 (AP) 記錄。")

    # 3. ➕ 登記新採購與應付帳款 (AP)
    with tab_ap_add:
        st.markdown(f"### {L['tab_ap_add']}")
        if st.session_state.supplier_db:
            auto_ap_no = f"AP-{datetime.date.today().year}-{len(st.session_state.ap_db)+1:03d}"
            vendor_names = [v["供應商名稱"] for v in st.session_state.supplier_db]

            with st.form("form_add_ap"):
                ac1, ac2 = st.columns(2)
                with ac1:
                    ap_no = st.text_input(L["lbl_ap_no"], value=auto_ap_no)
                    ap_vendor = st.selectbox(L["lbl_ap_vendor"], vendor_names)
                with ac2:
                    ap_amount = st.number_input(L["lbl_ap_amount"], min_value=0.0, value=5000.0, step=500.0)
                    ap_duedate = st.date_input(L["lbl_ap_duedate"], value=datetime.date.today() + datetime.timedelta(days=30))

                ap_desc = st.text_area(L["lbl_ap_desc"], placeholder="例如: 採購西寧廠配電盤五金零件一批")
                ap_status = st.selectbox(L["lbl_ap_status"], L["status_opts"])

                if st.form_submit_button(L["btn_add_ap"], type="primary", use_container_width=True):
                    if ap_no and ap_desc:
                        st.session_state.ap_db.append({
                            "AP單號": ap_no,
                            "供應商": ap_vendor,
                            "採購說明": ap_desc,
                            "應付金額": ap_amount,
                            "到期日": ap_duedate.strftime("%Y-%m-%d"),
                            "付款狀態": ap_status
                        })
                        st.success(L["success_add_ap"].format(no=ap_no))
                        st.rerun()
                    else:
                        st.warning("⚠️ 請完整填寫 AP 單號與採購說明！")
        else:
            st.warning("⚠️ 請先至「供應商分類與名冊管理」新增供應商，才可登記 AP！")

    # 4. 🔄 更新 AP 付款狀態
    with tab_ap_update:
        st.markdown(f"### {L['tab_ap_update']}")
        if st.session_state.ap_db:
            ap_options = {f"{ap.get('AP單號', '')} - {ap.get('供應商', '')} (${float(ap.get('應付金額', 0)):,.2f})": ap for ap in st.session_state.ap_db}
            sel_ap_key = st.selectbox("選擇要更新付款狀態的 AP 紀錄", list(ap_options.keys()))
            target_ap = ap_options[sel_ap_key]

            with st.form("form_update_ap_status"):
                st.write(f"**目前單號**：`{target_ap.get('AP單號')}`")
                st.write(f"**供應商**：{target_ap.get('供應商')}")
                st.write(f"**採購說明**：{target_ap.get('採購說明')}")
                st.write(f"**應付金額**：${float(target_ap.get('應付金額', 0)):,.2f} USD")
                
                curr_status = target_ap.get("付款狀態", L["status_opts"][0])
                status_idx = L["status_opts"].index(curr_status) if curr_status in L["status_opts"] else 0
                new_status = st.selectbox(L["lbl_ap_status"], L["status_opts"], index=status_idx)

                if st.form_submit_button("💾 確認更新付款進度", type="primary", use_container_width=True):
                    target_ap["付款狀態"] = new_status
                    st.success(f"✅ AP 單號 `{target_ap.get('AP單號')}` 付款狀態已更新為 `{new_status}`！")
                    st.rerun()
        else:
            st.info("目前無任何 AP 紀錄可供更新。")

# ----------------------------------------------------
# 🔗 相容性進入點定義（確保主程式呼叫不報錯）
# ----------------------------------------------------
def show(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def main(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)

def render_procurement_ap(*args, **kwargs):
    render_procurement_ap_page(*args, **kwargs)
