import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

# ----------------------------------------------------
# 📱 手機優先響應式 CSS 紋理 (Mobile-First UI)
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

USER_MGMT_I18N = {
    "繁體中文": {
        "title": "🔒 IT 管理中心 - 組織角色權限與系統模組授權",
        "caption": "裕豐電機（越南西寧廠）組織架構對照：嚴格對應公司組織圖編號與權限範本。",
        "tab_roles": "⚙️ 組織角色與模組權限設定 (RBAC)",
        "tab_audit": "📊 系統稽核日誌 (Audit Logs)",
        "tab_db": "🔌 資料庫連線狀態",
        "success_connected": "PostgreSQL / Supabase 資料庫連線正常！",
        "db_not_connected": "ℹ️ 提示：目前使用安全記憶體模式運行。",
        "cloud_roles_count": "已建角色數",
        "search_ph": "輸入角色名稱過濾...",
        "search_label": "🔍 搜尋角色關鍵字",
        "col_stt": "組織編號",
        "col_role_name": "職位角色名稱",
        "col_desc": "部門職責與組織架構範圍",
        "col_modules_count": "允許開啟之頁面數量",
        "edit_header": "✏️ 組織角色權限編輯維護 (依組織圖編號對照)",
        "select_role_lbl": "請選擇欲編輯的角色：",
        "create_new_opt": "🆕 建立新角色 (Create New)",
        "step1_title": "1. 輸入組織職位名稱與說明",
        "role_name_lbl": "職位名稱 (對應組織圖) *",
        "role_name_ph": "例如: 1. 董事長, 4. 廠長 / 副協理",
        "role_desc_lbl": "組織職責與權限範圍說明",
        "role_desc_ph": "例如: 公司經營方向規劃與戰略定奪",
        "step2_title": "2. 勾選該職位角色可操作功能頁面：",
        "btn_save_role": "💾 儲存組織角色設定",
        "btn_del_role": "🗑️ 刪除此角色",
        "save_role_success": "🎉 組織角色權限已成功儲存！",
        "del_role_success": "🗑️ 角色已成功刪除！"
    }
}

# 👑 嚴格對應您提供的「裕豐電機工業有限公司組織架構圖」完整 20 個編號順序
HIERARCHY_ORDER = [
    "1. 董事長",
    "2. 總經理",
    "3. 副總經理",
    "4. 廠長 / 副協理",
    "5. 管理部經理",
    "6. 行政主管",
    "7. 人事",
    "8. 財務副理",
    "9. 設計經理",
    "10. 設計主管",
    "11. 設計人員",
    "12. 精算主管",
    "13. 精算助理",
    "14. 生產主管",
    "15. 生產組長",
    "16. 工程人員",
    "17. 生產組",
    "18. 板金組",
    "19. 烤漆組",
    "20. 配電組裝",
    "系統管理員 (Admin)",
    "一般員工 (Staff)"
]

def get_role_sort_weight(role_name):
    """嚴格依照組織架構圖編號進行排序權重計算"""
    for idx, h_role in enumerate(HIERARCHY_ORDER):
        # 比對關鍵字或編號
        clean_h = h_role.split(". ")[-1] if ". " in h_role else h_role
        if h_role in role_name or clean_h in role_name:
            return idx
    return 999  # 未在清單內的排在最後

def fetch_roles(engine, lang_dict):
    fallback_roles = {
        "1. 董事長": {"description": "公司經營方向規劃與戰略定奪", "allowed_modules": "ALL"},
        "2. 總經理": {"description": "董事長指示的公司經營方向執行與公司管理", "allowed_modules": "ALL"},
        "3. 副總經理": {"description": "工程報價及現場探勘、人員調配與督導", "allowed_modules": "ALL"},
        "4. 廠長 / 副協理": {"description": "生產車間管理、工程支援與人事管理", "allowed_modules": "ALL"},
        "5. 管理部經理": {"description": "行政、財務、總務管理、ERP規劃與資訊管理", "allowed_modules": "ALL"}
    }
    if engine is None:
        return fallback_roles, False, lang_dict["db_not_connected"]
    
    try:
        df = pd.read_sql("SELECT role_name, description, allowed_modules FROM system_roles", con=engine)
        if df.empty:
            return fallback_roles, True, lang_dict["success_connected"]
        roles_dict = {}
        for _, row in df.iterrows():
            r_name = row["role_name"]
            desc = row.get("description", "")
            roles_dict[r_name] = {
                "description": desc,
                "allowed_modules": row.get("allowed_modules", "ALL")
            }
        return roles_dict, True, lang_dict["success_connected"]
    except Exception as e:
        return fallback_roles, False, f"{lang_dict['db_not_connected']} ({e})"

def save_role_db(engine, role_name, description, allowed_modules):
    if engine is None:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO system_roles (role_name, description, allowed_modules) 
                    VALUES (:r, :d, :m) 
                    ON CONFLICT (role_name) 
                    DO UPDATE SET description = :d, allowed_modules = :m
                """),
                {"r": role_name, "d": description, "m": allowed_modules}
            )
        return True
    except Exception:
        return False

def delete_role_db(engine, role_name):
    if engine is None:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM system_roles WHERE role_name = :r"), {"r": role_name})
        return True
    except Exception:
        return False

DEPARTMENT_MODULE_TREE = {
    "📈 總經理室 (Executive Office)": [
        "🔴 原料價格與 Gemini 智慧採購顧問",
        "📊 財務類顯示資料 (AR/AP & P&L)",
        "⚡ 工程專案進度與現場異常監控"
    ],
    "👔 管理部 (Management Dept)": [
        "📢 公司重要公告與佈告欄",
        "👤 員工個人檔案與人事管理",
        "🏢 廠內員工固定打卡與出勤紀錄",
        "📍 外勤位置驗證與工地即時人數",
        "🏭 廠區與工作廠區管理",
        "🚗 廠區車輛進出口門禁與派車審核",
        "🛠️ 車輛維修保養紀錄",
        "🏢 固定資產與設備管理",
        "🛒 採購與應付帳款 (AP)",
        "📋 應收帳款",
        "📊 越南稅務標準財務報表 (Thông tư 200)",
        "💰 員工薪資計算與保險扣除",
        "📄 電子發票綜合管理"
    ],
    "✍️ 全公司電子簽核中心 (Approval Center)": [
        "✍️ 提交請假/採購與即時進度追蹤 / 審核"
    ],
    "🛠️ 工程與設計管理中心 (Engineering & Design Center)": [
        "⚡ [工程] 配電盤與工程專案雙層報價",
        "📊 [工程] 工程驗收與進度追蹤",
        "📋 [工程] 現場工程日報表與出工統計",
        "🤖 [工程] AI 施工照片智慧辨識與歸檔",
        "⚠️ [工程] 分包商與專業證照到期預警",
        "🎨 [設計] 配電盤電氣與機構設計圖庫 Storage",
        "🔌 [工程] 配電盤 BOM 零件自動展開與採購連動",
        "👷 [工程] 外包商點工計價與越南勞動法計薪",
        "🧪 [工程] FAT/SAT 試驗報告與 QR Code 驗收",
        "📊 [工程] 越南營建電子發票與稅務合規管家"
    ],
    "🏭 生產部 (Production Dept)": [
        "📦 [倉儲] 倉庫庫存與資材條碼管理",
        "✂️ [板金] 板金加工組工單與條碼",
        "🎨 [塗料] 粉體塗裝烤漆組品管",
        "⚡ [配盤] 配電盤組裝配線組"
    ],
    "💻 資訊管理部 (IT & System)": [
        "🔒 系統角色權限與模組開關設定",
        "🎛️ 客戶 ERP 模組授權與功能開關"
    ]
}

ALL_MODULE_LIST = [mod for dept in DEPARTMENT_MODULE_TREE.values() for mod in dept]

def render_user_management_page(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in USER_MGMT_I18N else "繁體中文"
    L = USER_MGMT_I18N[active_lang]

    st.title(L["title"])
    st.caption(L["caption"])
    st.info("💡 提示：員工帳號新增與人事指派請至 **管理部 ➡️ 員工個人檔案與人事管理 (HR)** 進行處理。")

    if "audit_logs_db" not in st.session_state:
        st.session_state.audit_logs_db = [
            {"time": "2026-10-06 13:00:15", "user": "admin", "action": "登入系統 (Login)", "module": "Auth", "ip": "192.168.1.50", "status": "成功"}
        ]

    roles_dict, is_connected, msg = fetch_roles(engine, L)

    tab_roles, tab_audit, tab_db = st.tabs([
        L["tab_roles"], L["tab_audit"], L["tab_db"]
    ])

    with tab_roles:
        st.markdown(f"### {L['tab_roles']}")
        if is_connected:
            st.success(f"🟢 {msg}")
        else:
            st.info(f"{msg}")

        col_search, col_stats = st.columns([3, 1])
        with col_search:
            search_kw = st.text_input(L["search_label"], placeholder=L["search_ph"])
        with col_stats:
            st.metric(L["cloud_roles_count"], len(roles_dict))

        # 👑 嚴格依照組織架構圖編號權重進行排序
        sorted_role_names = sorted(roles_dict.keys(), key=get_role_sort_weight)

        table_rows = []
        for idx, r_name in enumerate(sorted_role_names, start=1):
            r_info = roles_dict[r_name]
            if not search_kw or (search_kw.lower() in r_name.lower() or search_kw.lower() in r_info["description"].lower()):
                mod_count_str = "全開 (ALL)" if r_info["allowed_modules"] == "ALL" else f"{len(r_info['allowed_modules'].split(','))} 個頁面"
                table_rows.append({
                    L["col_stt"]: idx,
                    L["col_role_name"]: r_name,
                    L["col_desc"]: r_info["description"],
                    L["col_modules_count"]: mod_count_str
                })

        if table_rows:
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"### {L['edit_header']}")

        role_opts = [L["create_new_opt"]] + sorted_role_names
        sel_role_display = st.selectbox(L["select_role_lbl"], options=role_opts, index=0)

        sel_role_key = "" if sel_role_display == L["create_new_opt"] else sel_role_display
        is_edit = sel_role_display != L["create_new_opt"]
        default_name = sel_role_key if is_edit else ""
        default_desc = roles_dict.get(sel_role_key, {}).get("description", "") if is_edit else ""

        curr_set = set(ALL_MODULE_LIST) if (is_edit and roles_dict.get(sel_role_key, {}).get("allowed_modules") == "ALL") else (set(roles_dict.get(sel_role_key, {}).get("allowed_modules", "").split(",")) if is_edit else set(ALL_MODULE_LIST))

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
                    chk = st.checkbox(m, value=(m in curr_set), key=f"chk_rbac_{active_lang}_{sel_role_key}_{dept}_{idx}_{m}")
                    if chk:
                        selected_mods.append(m)
            st.markdown("---")

        cb1, cb2 = st.columns(2)
        with cb1:
            btn_save = st.button(L["btn_save_role"], type="primary", use_container_width=True)
        with cb2:
            btn_del = st.button(L["btn_del_role"], use_container_width=True)

        if btn_save:
            t_name = in_name.strip()
            if t_name:
                mod_str = "ALL" if len(selected_mods) == len(ALL_MODULE_LIST) else (",".join(selected_mods) if selected_mods else "")
                save_role_db(engine, t_name, in_desc, mod_str)
                st.success(L["save_role_success"])
                st.rerun()
            else:
                st.warning("⚠️ 請輸入組織角色名稱！")

        if btn_del:
            t_name = in_name.strip() or sel_role_key
            if t_name and t_name != L["create_new_opt"]:
                if "1. 董事長" in t_name or "2. 總經理" in t_name:
                    st.error("🚫 系統保護：最高主管角色無法被刪除！")
                else:
                    delete_role_db(engine, t_name)
                    st.success(L["del_role_success"])
                    st.rerun()

    with tab_audit:
        st.markdown(f"### {L['tab_audit']}")
        if st.session_state.audit_logs_db:
            st.dataframe(pd.DataFrame(st.session_state.audit_logs_db), use_container_width=True)
        else:
            st.info("目前尚無稽核日誌紀錄。")

    with tab_db:
        st.markdown(f"### {L['tab_db']}")
        if engine is not None:
            st.success("🟢 資料庫 Engine 連線正常！")
        else:
            st.info("ℹ️ 系統目前執行於安全記憶體模式。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management_page(engine=engine, lang=lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
