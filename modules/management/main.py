# ==========================================
# 檔案路徑範例：modules/management/main.py (或對應的管理部主控台)
# 職責：管理部 L1 進入點，透過頂部子模組卡片列導覽，實現手機優先的分層架構
# ==========================================

import streamlit as st

def render(db_engine, lang='zh'):
    # 1. 頂部子模組分類導覽列（對應圖四的精美卡片按鈕）
    st.markdown("### 🏢 管理部 - 業務模組分層導覽")
    
    sub_modules = [
        {"id": "employee", "name": "員工管理", "desc": "越籍員工、外派幹部、合約與證件 90 天預警"},
        {"id": "attendance", "name": "考勤管理", "desc": "上下班打卡、請假與出勤異常審核"},
        {"id": "payroll", "name": "薪資管理", "desc": "薪資結構計算與 BHXH 社會保險扣繳"},
        {"id": "settings", "name": "人事設定", "desc": "部門參數、班別與合規設定"},
    ]

    # 初始化當前選中的子模組（預設為員工管理）
    if 'mgmt_active_sub' not in st.session_state:
        st.session_state['mgmt_active_sub'] = 'employee'

    # 渲染頂部卡片列
    cols = st.columns(len(sub_modules))
    for idx, sm in enumerate(sub_modules):
        is_active = (st.session_state['mgmt_active_sub'] == sm['id'])
        btn_type = "primary" if is_active else "secondary"
        
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"#### 📂 {sm['name']}")
                st.caption(sm['desc'])
                if st.button(f"進入該部門專區 ➡️", key=f"btn_sub_{sm['id']}", use_container_width=True, type=btn_type):
                    st.session_state['mgmt_active_sub'] = sm['id']
                    st.rerun()

    st.markdown("---")

    # 2. 根據選中的子模組動態渲染對應的專屬功能頁面
    active_sub = st.session_state['mgmt_active_sub']

    if active_sub == 'employee':
        # 載入員工管理子模組（包含您截圖中的新增、證件上傳、90天預警與總名冊）
        try:
            from modules.management.hr.employee.employee_profile import render as render_employee
            render_employee(db_engine, lang=lang)
        except Exception as e:
            st.error(f"載入員工管理模組失敗: {e}")

    elif active_sub == 'attendance':
        st.info("📌 [考勤管理模組] 載入中...（包含打卡、請假與異常審核）")
        # 可在此處載入對應的考勤渲染函式

    elif active_sub == 'payroll':
        st.info("📌 [薪資管理模組] 載入中...（包含薪資計算與 BHXH 保險報表）")
        # 可在此處載入對應的薪資渲染函式

    elif active_sub == 'settings':
        st.info("📌 [人事設定模組] 載入中...")
        # 可在此處載入對應的設定渲染函式
