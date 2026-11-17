# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：部門首頁與動態模組路由分發中心（工程部完整納入報價、倉庫成本連動與高層簽核流）
# ==========================================

import streamlit as st
from sqlalchemy import text

def render_dashboard(db_engine):
    current_dept = st.session_state.get('selected_dept', '總經理室')

    # 1. 總經理室專屬路由
    if current_dept == '總經理室':
        try:
            from modules.executive import executive_dashboard
            executive_dashboard.render_executive_main(engine=db_engine, lang='zh')
        except Exception as e:
            st.error(f"載入總經理室模組發生錯誤: {e}")
        return

    # 2. 工程部專屬路由（直出總覽戰情與完整拼圖模組）
    if current_dept == '工程部':
        st.markdown("### 🛠️ 工程部總覽與專案戰情中心 (Engineering Department Overview)")
        st.caption("彙整全廠高低壓配電盤案場、西寧與海防廠區施工進度、工程報價與多層級主管審核。")
        
        # 工程部核心 KPI 戰情總覽
        col_eng1, col_eng2, col_eng3, col_eng4 = st.columns(4)
        with col_eng1:
            st.metric(label="🏗️ 進行中案場總數", value="12 案", delta="+2 本月新增")
        with col_eng2:
            st.metric(label="⚡ 配電盤組裝進度達標率", value="91.8%", delta="+3.5%")
        with col_eng3:
            st.metric(label="📋 待審查設計圖紙", value="4 件", delta="進度正常")
        with col_eng4:
            st.metric(label="✍️ 待審核專案報價單", value="3 件", delta="送交副總/總經理")

        st.markdown("---")

        with st.expander("📌 工程部近期重要動土與案場進度回報", expanded=True):
            col_ep1, col_ep2 = st.columns(2)
            with col_ep1:
                st.markdown("**🏭 西寧廠二期配電盤車間：**")
                st.markdown("- 主體結構與高壓配電箱安裝：`施工中 (進度 85%)`")
            with col_ep2:
                st.markdown("**🏢 海防廠高壓配電迴路擴建：**")
                st.markdown("- 現場線路敷設與安檢測試：`預計 11/20 驗收`")

        st.markdown("---")
        st.markdown("### 📌 工程部專屬功能導覽與模組卡片")
        st.caption("💡 提示：以下卡片依據您在「系統設定 ➡️ 公司部門 ➡️ 跨群組彈性模組掛載」中所勾選的項目動態生成。")

        # 從資料庫撈取工程部掛載的模組
        mounted_feats_str = ""
        try:
            if db_engine:
                with db_engine.connect() as conn:
                    res = conn.execute(
                        text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d OR department_name = :d"),
                        {"d": '工程部'}
                    ).fetchone()
                    if res and res[0]:
                        mounted_feats_str = res[0]
        except Exception:
            pass

        if not mounted_feats_str:
            mounted_feats_str = "feat_eng_overview,feat_site_log,feat_blueprint,feat_eng_quotation,feat_eng_approval_flow"

        feature_list = [f.strip() for f in mounted_feats_str.split(",") if f.strip()]

        feature_meta_map = {
            "feat_eng_overview": {"name": "🛠️ 工程部總覽 / 專案進度追蹤", "desc": "高低壓配電盤案場與進度追蹤。"},
            "feat_site_log": {"name": "📋 工程報告與工地巡檢日報", "desc": "填報工地日報與現場巡檢。"},
            "feat_blueprint": {"name": "📐 設計圖紙上傳與審查", "desc": "管理工程設計藍圖與審查。"},
            "feat_eng_quotation": {"name": "💰 工程專案報價與倉庫成本連動", "desc": "報價時即時連動倉庫查詢物料庫存數量與成本金額，試算毛利。"},
            "feat_eng_approval_flow": {"name": "✍️ 協理估價與高層簽核中心", "desc": "協理填寫估價單後，自動送交副總與總經理填寫金額與最終審批。"}
        }

        cols = st.columns(2)
        for idx, feat_id in enumerate(feature_list):
            meta = feature_meta_map.get(feat_id, {"name": f"工程模組 ({feat_id})", "desc": "工程部專屬業務模組。"})
            col_target = cols[idx % 2]
            with col_target:
                with st.container(border=True):
                    st.markdown(f"#### {meta['name']}")
                    st.caption(meta['desc'])
                    if st.button("進入該模組專區 ➡️", key=f"main_enter_feat_{current_dept}_{feat_id}_{idx}", use_container_width=True, type="primary"):
                        st.session_state['current_view'] = 'dynamic_feature'
                        st.session_state['active_feature_id'] = feat_id
                        st.rerun()
        return

    # 3. 其他 L1 部門動態模組路由
    st.markdown(f"### 📁 當前部門：{current_dept}")
    st.caption("以下為該部門已掛載的業務模組卡片。")

    mounted_feats_str = ""
    try:
        if db_engine:
            with db_engine.connect() as conn:
                res = conn.execute(
                    text("SELECT mounted_features FROM sys_department_modules WHERE dept_name = :d OR department_name = :d"),
                    {"d": current_dept}
                ).fetchone()
                if res and res[0]:
                    mounted_feats_str = res[0]
    except Exception:
        pass

    if not mounted_feats_str:
        if '管理' in current_dept:
            mounted_feats_str = "feat_mgmt_supervisor,feat_announcements,feat_hr_employee,feat_hr_attendance,feat_hr_payroll,feat_ga,feat_fi"
        elif '生產' in current_dept:
            mounted_feats_str = "feat_prod_overview,feat_panel_build,feat_production_schedule"
        elif '倉庫' in current_dept:
            mounted_feats_str = "feat_warehouse_overview,feat_material,feat_barcode"
        else:
            mounted_feats_str = "feat_exec_announcements"

    feature_list = [f.strip() for f in mounted_feats_str.split(",") if f.strip()]

    feature_meta_map = {
        "feat_announcements": {"name": "📢 公司公告佈告欄管理", "desc": "管理部發布與管理公司公告。"},
        "feat_prod_overview": {"name": "🏭 生產部總覽 / 產線看板", "desc": "即時掌握產線運作狀況。"},
        "feat_panel_build": {"name": "⚡ 生產部 - 組裝與看板", "desc": "配電盤組裝進度與看板。"},
        "feat_production_schedule": {"name": "📅 生產進度與機台排程", "desc": "排定機台生產時程。"},
        "feat_warehouse_overview": {"name": "📦 倉庫管理總覽 / WMS", "desc": "WMS 智慧倉儲即時總覽。"},
        "feat_material": {"name": "📋 倉庫進出貨與料帳合一", "desc": "管理物料進出貨與庫存。"},
        "feat_barcode": {"name": "🏷️ 物料批次與條碼管理", "desc": "條碼掃描與批次追蹤。"},
        "feat_mgmt_supervisor": {"name": "🏢 管理部總覽 / 戰情室", "desc": "行政、人資與總務主管戰情中心。"},
        "feat_hr_employee": {"name": "👥 員工檔案與履約管理", "desc": "管理員工基本資料與合約。"},
        "feat_hr_attendance": {"name": "⏱️ 考勤與打卡紀錄管理", "desc": "GPS 外勤打卡與出勤統計。"},
        "feat_hr_payroll": {"name": "💰 薪資計算與保險 (BHXH)", "desc": "越籍員工薪資與保險計算。"},
        "feat_ga": {"name": "🛒 總務採購與應付帳款 (AP)", "desc": "請購、採購單與應付帳款管理。"},
        "feat_fi": {"name": "📊 財務會計與標準財報", "desc": "越南 Thông tư 200 會計標準財報。"},
        "feat_my_approvals": {"name": "✍️ 全公司電子表單簽核中心", "desc": "各類請假、採購與報銷審批。"}
    }

    cols = st.columns(2)
    for idx, feat_id in enumerate(feature_list):
        meta = feature_meta_map.get(feat_id, {"name": f"功能模組 ({feat_id})", "desc": "自定義業務功能模組。"})
        col_target = cols[idx % 2]
        with col_target:
            with st.container(border=True):
                st.markdown(f"#### {meta['name']}")
                st.caption(meta['desc'])
                if st.button("進入模組 ➡️", key=f"main_enter_feat_{current_dept}_{feat_id}_{idx}", use_container_width=True, type="primary"):
                    st.session_state['current_view'] = 'dynamic_feature'
                    st.session_state['active_feature_id'] = feat_id
                    st.rerun()
