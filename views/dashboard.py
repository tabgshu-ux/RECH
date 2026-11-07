# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：主選單與部門儀表板畫面渲染（已精簡、無重複標題）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_dashboard(db_engine):
    # 取得當前選擇的部門資訊（預設為管理部或第一個可用部門）
    if 'selected_dept_id' not in st.session_state:
        st.session_state['selected_dept_id'] = 'mgmt'

    current_dept_id = st.session_state['selected_dept_id']

    # 模擬部門清單結構
    departments = [
        {"id": "ceo", "name_zh": "總經理室", "name_vi": "Văn phòng Tổng Giám đốc", "level": "L1", "parent": None},
        {"id": "eng", "name_zh": "工程部", "name_vi": "Phòng Kỹ thuật", "level": "L1", "parent": None},
        {"id": "mgmt", "name_zh": "管理部", "name_vi": "Phòng Hành chính Quản trị", "level": "L1", "parent": None},
        {"id": "prod", "name_zh": "生產部", "name_vi": "Phòng Sản xuất", "level": "L1", "parent": None},
    ]

    current_target = next((d for d in departments if d['id'] == current_dept_id), departments[2])

    # -------------------------------------------------------------
    # 側邊欄：一級大部門導覽
    # -------------------------------------------------------------
    st.sidebar.markdown("### 🏢 企業組織樹狀導覽")
    st.sidebar.markdown("---")

    for dept in departments:
        is_selected = (dept['id'] == current_dept_id)
        btn_type = "primary" if is_selected else "secondary"
        
        # 側邊欄按鈕
        if st.sidebar.button(f"{dept['name_zh']} ({dept['name_vi']})", key=f"btn_dept_{dept['id']}", use_container_width=True, type=btn_type):
            st.session_state['selected_dept_id'] = dept['id']
            st.session_state['current_view'] = 'dashboard'
            st.session_state['active_feature_id'] = None
            st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True):
        st.session_state['current_view'] = 'dynamic_feature'
        st.session_state['active_feature_id'] = 'feat_it_menu'
        st.rerun()

    # -------------------------------------------------------------
    # 主畫面區域（已徹底清除頂部多餘的「企業導覽選單」大標題）
    # -------------------------------------------------------------

   # 若是管理部 L1，只保留最乾淨的主標題，徹底清除多餘的部門代碼與越文資訊列
    if current_target['id'] == 'mgmt':
        st.markdown("### 📂 管理部 - 功能儀表板")
        st.markdown("---")
        
        # 直接展開管理部主管綜合戰情儀表板
        try:
            from modules.management.supervisor_dashboard import render as render_supervisor
            render_supervisor(db_engine, lang=st.session_state.get('current_lang', 'zh'))
        except Exception as e:
            st.warning(f"戰情資料載入提示: {e}")
        st.markdown("---")

    # -------------------------------------------------------------
    # 該部門底下的業務模組卡片清單
    # -------------------------------------------------------------
    st.markdown("### 📌 此部門當前掛載的業務模組")
    
    if current_target['id'] == 'mgmt':
        features = [
            {"id": "feat_hr", "name": "人事行政 — 員工檔案與履約管理", "desc": "管理越籍員工、外派幹部證件與 90 天到期預警。"},
            {"id": "feat_attendance", "name": "人事行政 — 考勤與打卡紀錄", "desc": "日常上下班打卡、請假與出勤異常審核。"},
            {"id": "feat_payroll", "name": "人事行政 — 薪資計算與 BHXH 保險", "desc": "越南當地薪資結構、社會保險扣繳與報表。"},
        ]
        
        cols = st.columns(3)
        for idx, feat in enumerate(features):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"#### 📌 {feat['name']}")
                    st.caption(feat['desc'])
                    if st.button("進入功能 ➡️", key=f"btn_feat_{feat['id']}", use_container_width=True, type="primary"):
                        st.session_state['current_view'] = 'dynamic_feature'
                        st.session_state['active_feature_id'] = feat['id']
                        st.rerun()
    else:
        st.info(f"💡 [{current_target['name_zh']}] 相關業務模組建置中...")
