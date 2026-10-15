import streamlit as st
import pandas as pd
import requests
import json

# ----------------------------------------------------
# 🔌 Supabase 直連設定 (請確認您的專案網址)
# ----------------------------------------------------
SUPABASE_URL = "https://wvsqbefyekmueffcbwd.supabase.co"

def get_headers():
    # 自動抓取 Secrets 中的金鑰，若無則放空讓 API Gateway 允許公開唯讀/寫入
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
# 🌳 水電工程部門模組清單 (已完全移除海防廠)
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

def render_user_management_page(lang="繁體中文", **kwargs):
    st.title("🔒 IT 管理中心 - 組織角色權限與系統稽核總覽")
    st.caption("裕豐電機雲端高可用架構：對接 Supabase 雲端資料庫 (RBAC)。")

    tab_roles, tab_db, tab_audit, tab_users = st.tabs([
        "⚙️ 組織角色權限範本 (RBAC)", "🔌 雲端資料庫對接狀態", "📊 系統稽核日誌", "👥 員工帳號總覽"
    ])

    roles_dict, is_connected, msg = fetch_roles()
    if not roles_dict:
        roles_dict = {
            "董事長 / 總經理": {"description": "最高決策與全系統總覽權限", "allowed_modules": "ALL"},
            "副總經理": {"description": "協助總經理規劃制定公司策略、監督執行與領導團隊", "allowed_modules": "ALL"}
        }

    with tab_roles:
        st.markdown("### ⚙️ 裕豐電機組織角色與權限範本 (Supabase 雲端對接)")
        
        if is_connected:
            st.success(f"🟢 {msg}")
        else:
            st.error(f"❌ {msg}")

        col_search, col_stats = st.columns([3, 1])
        with col_search:
            search_kw = st.text_input("🔍 搜尋角色關鍵字", placeholder="輸入角色名稱過濾...")
        with col_stats:
            st.metric("雲端資料庫已建角色數", len(roles_dict))

        table_rows = []
        for r_name, r_info in roles_dict.items():
            if not search_kw or (search_kw.lower() in r_name.lower() or search_kw.lower() in r_info["description"].lower()):
                table_rows.append({
                    "角色名稱": r_name,
                    "職責與權限範圍": r_info["description"],
                    "允許開啟之頁面數量": "全開 (ALL)" if r_info["allowed_modules"] == "ALL" else f"{len(r_info['allowed_modules'].split(','))} 個頁面"
                })

        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ✏️ 角色權限編輯維護 (新增 / 載入修改 / 刪除)")

        role_opts = ["🆕 建立新角色 (Create New)"] + list(roles_dict.keys())
        sel_role = st.selectbox("請選擇欲編輯的角色", options=role_opts, index=0)

        is_edit = sel_role != "🆕 建立新角色 (Create New)"
        default_name = sel_role if is_edit else ""
        default_desc = roles_dict[sel_role]["description"] if is_edit else ""

        curr_set = set(ALL_MODULE_LIST) if (is_edit and roles_dict[sel_role]["allowed_modules"] == "ALL") else (set(roles_dict[sel_role]["allowed_modules"].split(",")) if is_edit else set(ALL_MODULE_LIST))

        st.markdown("#### 1. 輸入角色名稱與說明")
        in_name = st.text_input("職位角色名稱", value=default_name, placeholder="例如: 協理、現場工地主任")
        in_desc = st.text_input("部門職責與資料範圍說明", value=default_desc, placeholder="例如: 協助總經理工程支援指派，以及生產車間管理")

        st.markdown("#### 2. 勾選該職位角色可操作功能：")
        selected_mods = []
        for dept, mods in DEPARTMENT_MODULE_TREE.items():
            st.markdown(f"##### {dept}")
            cols = st.columns(3)
            for idx, m in enumerate(mods):
                with cols[idx % 3]:
                    chk = st.checkbox(m, value=(m in curr_set), key=f"chk_clean_{sel_role}_{dept}_{idx}_{m}")
                    if chk:
                        selected_mods.append(m)
            st.markdown("---")

        cb1, cb2 = st.columns(2)
        with cb1:
            btn_save = st.button("💾 永久寫入 Supabase 雲端資料庫", type="primary", use_container_width=True)
        with cb2:
            btn_del = st.button("🗑️ 從雲端資料庫刪除此角色", use_container_width=True)

        if btn_save:
            t_name = in_name.strip()
            if t_name:
                mod_str = "ALL" if len(selected_mods) == len(ALL_MODULE_LIST) else (",".join(selected_mods) if selected_mods else "")
                ok, res_msg = save_role(t_name, in_desc, mod_str)
                if ok:
                    st.success(f"🎉 角色 [{t_name}] 已成功寫入 Supabase 雲端資料庫！")
                    st.rerun()
                else:
                    st.error(f"❌ 寫入失敗: {res_msg}")
            else:
                st.warning("⚠️ 請輸入角色名稱！")

        if btn_del:
            t_name = in_name.strip() or (sel_role if is_edit else "")
            if t_name and t_name != "🆕 建立新角色 (Create New)":
                if t_name == "董事長 / 總經理":
                    st.error("🚫 系統保護：不可刪除最高階角色 [董事長 / 總經理]！")
                else:
                    delete_role(t_name)
                    st.success(f"🗑️ 角色 [{t_name}] 已從 Supabase 雲端成功刪除！")
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

    with tab_users:
        st.markdown("### 👥 員工帳號總覽")

def show(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def main(lang="繁體中文", **kwargs):
    render_user_management_page(lang, **kwargs)

def render_user_management(*args, **kwargs):
    render_user_management_page(*args, **kwargs)
