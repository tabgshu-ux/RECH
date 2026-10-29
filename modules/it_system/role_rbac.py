import streamlit as st
import pandas as pd
from sqlalchemy import text

# 手機優先響應式設計
MOBILE_CSS = """
<style>
@media only screen and (max-width: 768px) {
    h1 { font-size: 1.25rem !important; }
    h2 { font-size: 1.1rem !important; }
    h3 { font-size: 1.0rem !important; }
    p, div, span, label { font-size: 0.9rem !important; }
    .stButton button { width: 100% !important; min-height: 44px !important; }
}
</style>
"""
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

RBAC_I18N = {
    "繁體中文": {
        "title": "⚙️ 組織角色與權限指派中心 (RBAC)",
        "caption": "定義職位角色與部門關聯，並勾選可操作頁面，供人事模組進行員工工作指派。",
        "role_name": "職位角色名稱",
        "dept_name": "所屬部門",
        "desc": "職責說明與範圍",
        "save_btn": "💾 儲存角色權限設定",
        "delete_btn": "🗑️ 刪除此角色",
        "success_save": "🎉 角色權限已成功儲存至資料庫！",
        "success_del": "🗑️ 角色已成功刪除！"
    },
    "Tiếng Việt": {
        "title": "⚙️ Trung tâm Phân quyền Vai trò (RBAC)",
        "caption": "Định nghĩa vai trò công việc và phân quyền module cho nhân sự.",
        "role_name": "Tên vai trò",
        "dept_name": "Phòng ban",
        "desc": "Mô tả công việc",
        "save_btn": "💾 Lưu phân quyền",
        "delete_btn": "🗑️ Xóa vai trò",
        "success_save": "🎉 Đã lưu cấu hình vai trò thành công!",
        "success_del": "🗑️ Đã xóa vai trò thành công!"
    },
    "English": {
        "title": "⚙️ Role & Permission Assignment Center (RBAC)",
        "caption": "Define job roles, department association, and module permissions for HR assignment.",
        "role_name": "Role Name",
        "dept_name": "Department",
        "desc": "Description & Scope",
        "save_btn": "💾 Save Role Permissions",
        "delete_btn": "🗑️ Delete Role",
        "success_save": "🎉 Role permissions saved successfully!",
        "success_del": "🗑️ Role deleted successfully!"
    }
}

def render(engine=None, lang="繁體中文", **kwargs):
    active_lang = lang if lang in RBAC_I18N else "繁體中文"
    L = RBAC_I18N[active_lang]

    st.markdown(f"### {L['title']}")
    st.caption(L['caption'])

    # 初始化資料表
    if engine is not None:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS system_roles (
                        id SERIAL PRIMARY KEY,
                        role_name VARCHAR(100) UNIQUE NOT NULL,
                        department VARCHAR(150) DEFAULT '管理部 (Management Dept)',
                        description TEXT,
                        allowed_modules TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                """))
        except Exception:
            pass

    # 讀取現有角色資料
    roles_data = {}
    if engine is not None:
        try:
            df = pd.read_sql("SELECT role_name, department, description, allowed_modules FROM system_roles", con=engine)
            for _, row in df.iterrows():
                roles_data[row["role_name"]] = {
                    "department": row["department"],
                    "description": row["description"],
                    "allowed_modules": row["allowed_modules"]
                }
        except Exception:
            pass

    if not roles_data:
        roles_data = {
            "外勤技師": {"department": "🛠️ 工程與設計管理中心 (Engineering & Design Center)", "description": "負責現場外勤打卡與施工回報", "allowed_modules": "📍 3. 現場外勤打卡與作業登記"},
            "人事專員": {"department": "👔 管理部 (Management Dept)", "description": "負責員工檔案與考勤薪資管理", "allowed_modules": "👤 員工個人檔案與人事管理,💰 員工薪資計算與保險扣除"}
        }

    departments_list = [
        "📈 總經理室 (Executive Office)",
        "👔 管理部 (Management Dept)",
        "🛠️ 工程與設計管理中心 (Engineering & Design Center)",
        "🏭 生產部 (Production Dept)",
        "📦 倉庫管理 (Warehouse Management)",
        "💻 資訊管理部 (IT & System)"
    ]

    master_modules = [
        "🔴 原料價格與 Gemini 智慧採購顧問", "📊 財務類顯示資料 (AR/AP & P&L)",
        "⚡ 工程專案進度與現場異常監控", "📰 越南經營政策與法規每日動態",
        "📢 發送公告佈告欄", "👤 員工個人檔案與人事管理",
        "🏢 廠內員工固定打卡與出勤紀錄", "📍 外勤位置辦理與工地即時人數",
        "🥗 幹部宿舍伙食與採購控管", "🏭 工作廠區管理",
        "🚗 廠區車輛進出口門禁與派車審核", "🛠️ 車輛維修保養紀錄",
        "🏢 固定資產與設備管理", "🛒 採購與應付帳款 (AP)",
        "📋 應收帳款與對帳管理中心", "📊 越南稅務標準財務報表 (Thông tư 200)",
        "💰 員工薪資計算與保險扣除", "📄 電子發票綜合管理與 XML 歸檔",
        "✍️ 提交請假/採購與即時進度追蹤 / 審核", "⚡ 1. 工程主管戰情室與案場管理",
        "⚡ 2. 工程專案報價系統", "📍 3. 現場外勤打卡與作業登記",
        "📋 4. 施工日報表與點工點料登記", "🤖 5. AI 施工照片辨識與稽核",
        "⚠️ 6. 工程證照預警與機具檢驗預警", "🎨 7. 配電盤電氣與機構設計圖庫",
        "🔌 8. 配電盤 BOM 零件與採購連動", "👷 9. 外包商計價與偶鐸管理",
        "🧪 10. FAT/SAT 出廠與現場驗收管理", "📦 [倉儲] 倉庫庫存與資材條碼管理",
        "✂️ [板金] 板金加工組工單與條碼", "🎨 [塗料] 粉體塗裝烤漆組品管",
        "⚡ [配盤] 配電盤組裝配線組", "🔒 系統角色權限與模組開關設定",
        "🔌 API 串聯設定中心"
    ]

    role_options = ["🆕 建立新工作角色"] + sorted(list(roles_data.keys()))
    selected_role_opt = st.selectbox("🎯 選擇欲編輯或新增的工作角色 / Select Role:", role_options)

    is_edit = selected_role_opt != "🆕 建立新工作角色"
    default_name = selected_role_opt if is_edit else ""
    default_dept = roles_data.get(selected_role_opt, {}).get("department", departments_list[0]) if is_edit else departments_list[0]
    default_desc = roles_data.get(selected_role_opt, {}).get("description", "") if is_edit else ""
    current_allowed = roles_data.get(selected_role_opt, {}).get("allowed_modules", "") if is_edit else ""
    current_allowed_set = set(current_allowed.split(",")) if current_allowed else set()

    with st.form("role_rbac_form"):
        role_name_input = st.text_input(L['role_name'] + " *", value=default_name, placeholder="例如: 外勤技師, 產線班長, 人事主管")
        
        dept_idx = departments_list.index(default_dept) if default_dept in departments_list else 0
        dept_select = st.selectbox(L['dept_name'] + " *", options=departments_list, index=dept_idx)
        
        desc_input = st.text_input(L['desc'], value=default_desc, placeholder="例如: 負責工地外勤打卡與回報")

        st.markdown("---")
        st.markdown("#### 🧩 勾選此角色可操作的功能模組（供人事指派使用）：")

        selected_mods = []
        cols = st.columns(2)
        for idx, mod_item in enumerate(master_modules):
            with cols[idx % 2]:
                chk_key = f"rbac_mod_{selected_role_opt}_{idx}_{mod_item}"
                init_checked = mod_item in current_allowed_set
                if st.checkbox(mod_item, value=init_checked, key=chk_key):
                    selected_mods.append(mod_item)

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            submitted = st.form_submit_button(L['save_btn'], type="primary", use_container_width=True)
        with col_sub2:
            deleted = st.form_submit_button(L['delete_btn'], use_container_width=True)

        if submitted:
            r_name = role_name_input.strip()
            if r_name:
                mod_str = ",".join(selected_mods)
                if engine is not None:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO system_roles (role_name, department, description, allowed_modules)
                                VALUES (:r, :dept, :d, :m)
                                ON CONFLICT (role_name)
                                UPDATE SET department = :dept, description = :d, allowed_modules = :m;
                            """), {"r": r_name, "dept": dept_select, "d": desc_input, "m": mod_str})
                    except Exception as e:
                        st.error(f"資料庫儲存失敗: {str(e)}")
                st.success(L['success_save'])
                st.rerun()
            else:
                st.warning("⚠️ 請輸入有效的職位角色名稱！")

        if deleted and is_edit:
            if selected_role_opt in ["系統管理員 (Admin)", "admin"]:
                st.error("🚫 系統核心角色無法刪除！")
            else:
                if engine is not None:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM system_roles WHERE role_name = :r"), {"r": selected_role_opt})
                    except Exception:
                        pass
                st.success(L['success_del'])
                st.rerun()

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
