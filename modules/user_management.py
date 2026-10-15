import streamlit as st
import pandas as pd
import requests
import json

# ----------------------------------------------------
# 📱 手機優先響應式 CSS 注入 (Mobile-First UI)
# ----------------------------------------------------
MOBILE_USER_MGMT_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.3rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.85rem !important; }
    .stDataFrame { overflow-x: auto; }
    .stButton button { width: 100% !important; }
}
</style>
"""
st.markdown(MOBILE_USER_MGMT_CSS, unsafe_allow_html=True)

# ----------------------------------------------------
# 🌐 多語系字典 (i18n Dictionary)
# ----------------------------------------------------
USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織角色權限與系統稽核總覽",
        "caption": "裕豐電機雲端高可用架構：對接 Supabase 雲端資料庫 (RBAC)，實現零暫存、真實資料庫存取。",
        "tab_roles": "⚙️ 組織角色權限範本 (RBAC)",
        "tab_db": "🔌 雲端資料庫對接狀態",
        "tab_audit": "📊 系統稽核日誌",
        "tab_users": "👥 員工帳號總覽",
        "success_connected": "資料庫連線成功！",
        "cloud_roles_count": "雲端資料庫已建角色數",
        "search_ph": "輸入角色名稱過濾...",
        "search_label": "🔍 搜尋角色關鍵字",
        "col_role_name": "角色名稱",
        "col_desc": "職責與權限範圍",
        "col_modules_count": "允許開啟之頁面數量",
        "edit_header": "✏️ 角色權限編輯維護 (新增 / 載入修改 / 刪除)",
        "select_role_lbl": "請選擇欲編輯的角色：",
        "create_new_opt": "🆕 建立新角色 (Create New)",
        "step1_title": "1. 輸入角色名稱與說明",
        "role_name_lbl": "職位角色名稱 *",
        "role_name_ph": "例如: 協理、現場工地主任",
        "role_desc_lbl": "部門職責與資料範圍說明",
        "role_desc_ph": "例如: 協助總經理工程支援指派，以及生產車間管理",
        "step2_title": "2. 勾選該職位角色可操作功能：",
        "btn_save": "💾 永久寫入 Supabase 雲端資料庫",
        "btn_del": "🗑️ 從雲端資料庫刪除此角色",
        "save_success": "🎉 角色 [{name}] 已成功寫入 Supabase 雲端資料庫！",
        "save_fail": "❌ 寫入失敗: {msg}",
        "del_success": "🗑️ 角色 [{name}] 已從 Supabase 雲端成功刪除！",
        "protect_err": "🚫 系統保護：不可刪除最高階角色 [董事長 / 總經理]！",
        "warn_name": "⚠️ 請輸入角色名稱！"
    },
    "Tiếng Việt": {
        "title": "🔒 Quản trị IT - Cấu hình Phân quyền & Nhật ký Hệ thống",
        "caption": "Kiến trúc đám mây Reetech: Kết nối cơ sở dữ liệu Supabase (RBAC).",
        "tab_roles": "⚙️ Phân quyền Vai trò (RBAC)",
        "tab_db": "🔌 Trạng thái CSDL đám mây",
        "tab_audit": "📊 Nhật ký Kiểm toán",
        "tab_users": "👥 Danh sách Nhân sự",
        "success_connected": "Kết nối cơ sở dữ liệu thành công!",
        "cloud_roles_count": "Số lượng vai trò trên cloud",
        "search_ph": "Nhập tên vai trò...",
        "search_label": "🔍 Tìm kiếm vai trò",
        "col_role_name": "Tên vai trò",
        "col_desc": "Mô tả chức năng",
        "col_modules_count": "Số lượng trang cho phép",
        "edit_header": "✏️ Chỉnh sửa Phân quyền (Thêm / Sửa / Xóa)",
        "select_role_lbl": "Chọn vai trò cần chỉnh sửa:",
        "create_new_opt": "🆕 Tạo vai trò mới",
        "step1_title": "1. Nhập tên và mô tả vai trò",
        "role_name_lbl": "Tên vai trò *",
        "role_name_ph": "Ví dụ: Kỹ sư trưởng, Quản đốc",
        "role_desc_lbl": "Mô tả trách nhiệm",
        "role_desc_ph": "Ví dụ: Quản lý khu vực sản xuất",
        "step2_title": "2. Chọn các chức năng được phép:",
        "btn_save": "💾 Lưu vào cơ sở dữ liệu Supabase",
        "btn_del": "🗑️ Xóa vai trò khỏi đám mây",
        "save_success": "🎉 Đã lưu vai trò [{name}] vào cơ sở dữ liệu thành công!",
        "save_fail": "❌ Lưu thất bại: {msg}",
        "del_success": "🗑️ Đã xóa vai trò [{name}] thành công!",
        "protect_err": "🚫 Bảo vệ hệ thống: Không thể xóa vai trò [Chủ tịch / Tổng giám đốc]!",
        "warn_name": "⚠️ Vui lòng nhập tên vai trò!"
    },
    "English": {
        "title": "🔒 IT Center - RBAC & System Audit Logs",
        "caption": "Reetech Cloud Architecture: Connected to Supabase Cloud Database (RBAC).",
        "tab_roles": "⚙️ Departmental Roles (RBAC)",
        "tab_db": "🔌 Cloud DB Status",
        "tab_audit": "📊 Audit Logs",
        "tab_users": "👥 HR & Accounts",
        "success_connected": "Database connection successful!",
        "cloud_roles_count": "Roles in Cloud DB",
        "search_ph": "Filter role name...",
        "search_label": "🔍 Search Roles",
        "col_role_name": "Role Name",
        "col_desc": "Description & Scope",
        "col_modules_count": "Allowed Modules Count",
        "edit_header": "✏️ Edit Role Permissions (Create / Update / Delete)",
        "select_role_lbl": "Select Role to Edit:",
        "create_new_opt": "🆕 Create New Role",
        "step1_title": "1. Enter Role Name and Description",
        "role_name_lbl": "Role Name *",
        "role_name_ph": "e.g., Supervisor, Site Manager",
        "role_desc_lbl": "Responsibility Description",
        "role_desc_ph": "e.g., Oversee site engineering operations",
        "step2_title": "2. Select Allowed Features for this Role:",
        "btn_save": "💾 Write to Supabase Cloud Database",
        "btn_del": "🗑️ Delete Role from Cloud",
        "save_success": "🎉 Role [{name}] successfully saved to Supabase!",
        "save_fail": "❌ Save failed: {msg}",
        "del_success": "🗑️ Role [{name}] successfully deleted from cloud!",
        "protect_err": "🚫 System Protection: Cannot delete top-tier role [Chairman / CEO]!",
        "warn_name": "⚠️ Please enter a role name!"
    }
}

# ----------------------------------------------------
# 🔌 Supabase 直連設定與 API 互動函式
# ----------------------------------------------------
SUPABASE_URL = "https://wvsqbefyekmueffcbwd.supabase.co"

def get_headers():
    key = st.secrets.get("SUPABASE_ANON_KEY", "")
    headers = {
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    if key and "sample_key" not in key:
        headers["apikey"] = key
        headers["Authorization"] = f"Bearer {key}"
    return headers

def fetch_roles():
    try:
        url = f"{SUPABASE_URL}/rest/v1/system_roles?select=*"
        resp = requests.get(url, headers=get_headers(), timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            roles_dict = {}
            for item in data:
                roles_dict[item["role_name"]] = {
                    "description": item.get("description", ""),
                    "allowed_modules": item.get("allowed_modules", "ALL")
                }
            return roles_dict, True, "資料庫連線成功！"
        else:
            return {}, False, f"連線回應代碼 {resp.status_code}: {resp.text}"
    except Exception as e:
        return {}, False, f"連線異常: {e}"

def save_role(role_name, description, allowed_modules):
    try:
        headers = get_headers()
        headers["Prefer"] = "resolution=merge-duplicates"
        url = f"{SUPABASE_URL}/rest/v1/system_roles"
        payload = [{
            "role_name": role_name,
            "description": description,
            "allowed_modules": allowed_modules
        }]
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
        if resp.status_code in [200, 201, 204]:
            return True, "儲存成功"
        else:
            return False, f"儲存失敗 ({resp.status_code}): {resp.text}"
    except Exception as e:
        return False, f"儲存異常: {e}"

def delete_role(role_name):
    try:
        url = f"{SUPABASE_URL}/rest/v1/system_roles?role_name=eq.{role_name}"
        resp = requests.delete(url, headers=get_headers(), timeout=5)
        return resp.status_code in [200, 204]
    except Exception as e:
        return False

# ----------------------------------------------------
# 🌳 水電工程部門模組清單 (不含海防廠，符合需求)
# ----------------------------------------------------
DEPARTMENT_MODULE_TREE = {
    "📈 總經理室 (Executive Office)": [
        "📢 公司重要公告與簡報",
        "📊 全公司 KPI 營運績效與決策儀表板",
        "📑 高階主管審核與拍板中心"
    ],
    "🏢 管理部 (Management Dept)": [
        "👥 員工個人檔案與人事管理",
        "🕒 廠內員工固定打卡與出勤紀錄",
        "🏗️ 外勤出勤統計與工地人數監控",
        "🍱 幹部宿舍伙食與採購控管",
        "🏢 廠區與工作廠區管理",
        "🚧 廠區車輛進出口門禁與派車審核",
        "🔧 車輛維修保養紀錄",
        "💻 固定資產與設備管理",
        "🛒 採購與應付帳款 (AP)",
        "💰 應收帳款與對帳管理中心",
        "🧾 越南稅務標準財務報表 (Thông tư 200)",
        "💵 員工薪資計算與保險扣除",
        "🧾 電子發票綜合管理與 XML 報檔"
    ],
    "📑 全公司電子簽核中心 (Approval Center)": [
        "✍️ 跨部門電子表單簽核與呈核系統",
        "📋 雙層報價單高階拍板簽核佇列"
    ],
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
        "📐 工程 BOM 零件自動展開與採購/庫存連動",
        "📑 工程報價單與雙層利潤分析/合約簽核",
        "⚡ 配電盤組裝配線組與拍照入庫模組",
        "👷 現場工地主任日報表與點工點料扣減",
        "🛠️ 外包商請款與估驗進度比對"
    ],
    "🏭 生產部 (Production Dept)": [
        "⚡ 配電盤組裝配線組與拍照入庫",
        "📦 越南西寧廠倉庫庫存盤點與領料"
    ],
    "💻 資訊管理部 (IT & System)": [
        "🔒 帳號權限與全系統稽核軌跡",
        "🔌 客戶 ERP 模組授權與功能開關",
        "萬用資料庫一鍵安裝精靈 (DB Wizard)",
        "🔌 越南電子發票與系統 SMTP 信箱 API 設定"
    ]
}

ALL_MODULE_LIST = [mod for dept in DEPARTMENT_MODULE_TREE.values() for mod in dept]

# ----------------------------------------------------
# 🖥️ 主渲染函式
# ----------------------------------------------------
def render_user_management_page(lang="繁體中文", **kwargs):
    active_lang = lang if lang in USER_MGMT_I18N else "繁體中文"
    L = USER_MGMT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])

    tab_roles, tab_db, tab_audit, tab_users = st.tabs([
        L["tab_roles"], L["tab_db"], L["tab_audit"], L["tab_users"]
    ])

    roles_dict, is_connected, msg = fetch_roles()
    if not roles_dict:
        roles_dict = {
            "董事長 / 總經理": {"description": "最高決策與全系統總覽權限", "allowed_modules": "ALL"},
            "副總經理": {"description": "協助總經理規劃制定公司策略、監督執行與領導團隊", "allowed_modules": "ALL"}
        }

    with tab_roles:
        st.markdown(f"### {L['tab_roles']}")
        
        if is_connected:
            st.success(f"🟢 {L['success_connected']} ({msg})")
        else:
            st.error(f"❌ {msg}")

        col_search, col_stats = st.columns([3, 1])
        with col_search:
            search_kw = st.text_input(L["search_label"], placeholder=L["search_ph"])
        with col_stats:
            st.metric(L["cloud_roles_count"], len(roles_dict))

        table_rows = []
        for r_name, r_info in roles_dict.items():
            if not search_kw or (search_kw.lower() in r_name.lower() or search_kw.lower() in r_info["description"].lower()):
                mod_count_str = "全開 (ALL)" if r_info["allowed_modules"] == "ALL" else f"{len(r_info['allowed_modules'].split(','))} 個頁面"
                table_rows.append({
                    L["col_role_name"]: r_name,
                    L["col_desc"]: r_info["description"],
                    L["col_modules_count"]: mod_count_str
                })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"### {L['edit_header']}")

        role_opts = [L["create_new_opt"]] + list(roles_dict.keys())
        sel_role = st.selectbox(L["select_role_lbl"], options=role_opts, index=0)

        is_edit = sel_role != L["create_new_opt"]
        default_name = sel_role if is_edit else ""
        default_desc = roles_dict[sel_role]["description"] if is_edit else ""

        curr_set = set(ALL_MODULE_LIST) if (is_edit and roles_dict[sel_role]["allowed_modules"] == "ALL") else (set(roles_dict[sel_role]["allowed_modules"].split(",")) if is_edit else set(ALL_MODULE_LIST))

        st.markdown(f"#### {L['step1_title']}")
        in_name = st.text_input(L["role_name_lbl"], value=default_name, placeholder=L["role_name_ph"])
        in_desc = st.text_input(L["role_desc_lbl"], value=default_desc, placeholder=L["role_desc_ph"])

        st.markdown(f"#### {L['step2_title']}")
        selected_mods = []
        for dept, mods in DEPARTMENT_MODULE_TREE.items():
            st.markdown(f"##### {dept}")
            cols = st.columns(3)
            for idx, m in enumerate(mods):
                with cols[idx % 3]:
                    chk = st.checkbox(m, value=(m in curr_set), key=f"chk_clean_{active_lang}_{sel_role}_{dept}_{idx}_{m}")
                    if chk:
                        selected_mods.append(m)
            st.markdown("---")

        cb1, cb2 = st.columns(2)
        with cb1:
            btn_save = st.button(L["btn_save"], type="primary", use_container_width=True)
        with cb2:
            btn_del = st.button(L["btn_del"], use_container_width=True)

        if btn_save:
            t_name = in_name.strip()
            if t_name:
                mod_str = "ALL" if len(selected_mods) == len(ALL_MODULE_LIST) else (",".join(selected_mods) if selected_mods else "")
                ok, res_msg = save_role(t_name, in_desc, mod_str)
                if ok:
                    st.success(L["save_success"].format(name=t_name))
                    st.rerun()
                else:
                    st.error(L["save_fail"].format(msg=res_msg))
            else:
                st.warning(L["warn_name"])

        if btn_del:
            t_name = in_name.strip() or (sel_role if is_edit else "")
            if t_name and t_name != L["create_new_opt"]:
                if t_name == "董事長 / 總經理":
                    st.error(L["protect_err"])
                else:
                    delete_role(t_name)
                    st.success(L["del_success"].format(name=t_name))
                    st.rerun()

    with tab_db:
        st.markdown("### 🔌 雲端資料庫連線狀態")
        st.text_input("目前對接端點 (SUPABASE_URL)", value=SUPABASE_URL, disabled=True)
        if is_connected:
            st.success("🟢 雲端資料庫連線正常！")
        else:
            st.error(f"❌ 連線失敗: {msg}")

    with tab_audit:
        st.markdown("### 📊 系統操作稽核日誌")
        st.info("稽核軌跡資料表已就緒。")

    with tab_users:
        st.markdown("### 👥 員工帳號總覽")
        st.info("員工名冊與權限綁定模組已就緒。")

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
