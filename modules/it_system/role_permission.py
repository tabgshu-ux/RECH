# ==========================================
# 檔案路徑：modules/it_system/role_permission.py
# 職責：組織角色與權限指派中心（RBAC - 依部門動態過濾模組，避免大海撈針）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render(engine=None, lang="繁體中文", **kwargs):
    st.subheader("⚙️ 組織角色與權限指派中心 (RBAC)")
    st.info("採用模組化分類管理，並依所屬部門自動過濾對應模組，讓權限指派更精準。")

    departments = [
        {"code": "ceo", "name": "👑 總經理室 (Executive Office)"},
        {"code": "mgmt", "name": "👔 管理部 (Management Department)"},
        {"code": "eng", "name": "🛠️ 工程部 (Engineering Department)"},
        {"code": "prod", "name": "🏭 生產部 (Production Department)"},
        {"code": "warehouse", "name": "📦 倉庫管理 (Warehouse Department)"},
        {"code": "approval", "name": "✍️ 簽核中心 (Approval Center)"},
        {"code": "it", "name": "⚙️ 系統與 IT 核心設定"}
    ]
    dept_options = {d["name"]: d["code"] for d in departments}

    st.markdown("---")
    st.markdown("#### 🎯 選擇欲編輯或新增的工作角色 / Select Role:")
    
    role_mode = st.selectbox("操作模式", ["建立新工作角色", "編輯現有角色權限"])
    
    col1, col2 = st.columns(2)
    with col1:
        role_name = st.text_input("職位角色名稱 *", placeholder="例如: 現場工程師、倉庫主管")
    with col2:
        selected_dept_label = st.selectbox("所屬部門 *", options=list(dept_options.keys()))
        selected_dept_code = dept_options[selected_dept_label]

    role_desc = st.text_area("職責說明與範圍", placeholder="例如: 負責工地現場日報登記、點工點料回報與損益追蹤")

    st.markdown("---")
    st.markdown("#### 🧩 模組拼圖權限指派（依部門自動聯動過濾）：")
    st.info(f"💡 當前選定部門：**{selected_dept_label}**。系統已為您自動過濾並聚焦該部門專屬的業務模組，亦可展開其他部門進行跨部門支援授權。")

    DEPARTMENT_MODULE_MAPPING = {
        "ceo": {
            "category": "👑 總經理室與決策戰情",
            "modules": [
                "總經理室總覽",
                "AI 原料採購顧問與金屬行情",
                "工程進度與異常即時監控",
                "財務與金流總覽 (AR / AP & P&L)",
                "工程案場與金額佔比分析"
            ]
        },
        "mgmt": {
            "category": "👔 管理部總覽與後勤支援",
            "modules": [
                "管理部總覽",
                "公司公告佈告欄",
                "人事行政課 — 員工檔案與履約管理",
                "人事行政課 — 考勤與打卡紀錄",
                "人事行政課 — 薪資計算與 BHXH 保險",
                "總務採購課 — 採購單與應付帳款 (AP)",
                "財務會計課 — 應收帳款管理 (AR) 與財報"
            ]
        },
        "eng": {
            "category": "🛠️ 工程與現場作業管理",
            "modules": [
                "工程部總覽",
                "工程專案損益與預算控管",
                "工程專案報價系統",
                "施工日報表與點工點料登記",
                "配電盤電氣與機構設計圖庫"
            ]
        },
        "prod": {
            "category": "🏭 生產製造與倉庫管理",
            "modules": [
                "生產部總覽",
                "倉庫庫存與資材條碼管理",
                "配電盤組裝配線組進度追蹤"
            ]
        },
        "approval": {
            "category": "✍️ 跨部門電子簽核中心",
            "modules": [
                "跨部門電子簽核中心主控台",
                "待簽核單據彙整與主管簽核"
            ]
        },
        "it": {
            "category": "⚙️ 系統與 IT 核心設定",
            "modules": [
                "公司組織架構與 L1~L4 動態配置中心"
            ]
        }
    }

    assigned_modules = []

    for dept_code, group_info in DEPARTMENT_MODULE_MAPPING.items():
        is_primary_dept = (dept_code == selected_dept_code)
        expander_label = f"{group_info['category']} {'⭐ [該角色所屬主部門專屬]' if is_primary_dept else ''}"
        
        with st.expander(expander_label, expanded=is_primary_dept):
            for mod_name in group_info["modules"]:
                default_check = is_primary_dept and ("總覽" in mod_name)
                if st.checkbox(f"**{mod_name}**", value=default_check, key=f"perm_{selected_dept_code}_{mod_name}"):
                    assigned_modules.append(mod_name)

    st.markdown("---")
    if st.button("💾 儲存並指派角色權限", type="primary", use_container_width=True):
        if not role_name:
            st.error("⚠️ 請填寫職位角色名稱！")
        else:
            st.success(f"🎉 成功儲存角色 [{role_name}]！已指派 {len(assigned_modules)} 項模組權限至 [{selected_dept_label}]。")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
