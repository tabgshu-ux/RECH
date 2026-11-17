# ==========================================
# 檔案路徑：views/dashboard.py
# 職責：部門首頁與動態模組路由分發中心（嚴格過濾僅顯示 L1 級頂級部門）
# ==========================================

import streamlit as st
from sqlalchemy import text

def render_dashboard(db_engine):
    # 🌟 側邊欄：嚴格只允許 L1 級頂級大部門與特定角色入口
    with st.sidebar:
        st.markdown("### 🏢 企業組織樹狀導航")
        st.caption("僅顯示 L1 核心一級部門，L2 子部門與課別納入管理。")
        
        # 動態讀取資料庫中的部門，並嚴格過濾只抓取 L1 級部門
        depts = []
        try:
            if db_engine:
                with db_engine.connect() as conn:
                    # 優先讀取資料庫中被標記為 L1 或屬於一級部門的清單
                    res = conn.execute(text("""
                        SELECT dept_name_zh, dept_name, name, level_tier 
                        FROM sys_departments 
                        WHERE is_active = TRUE
                    """)).fetchall()
                    
                    for r in res:
                        d_name = r[0] or r[1] or r[2] or '未命名部門'
                        tier = str(r[3] or 'L1').upper()
                        
                        # 🌟 核心過濾：只允許 L1 級部門，或者明確屬於三大塊的名稱，徹底排除 L2 子部門
                        is_l1 = ('L1' in tier) or (d_name in ["總經理室", "工程部", "管理部", "生產部", "倉庫管理", "簽核中心"])
                        exclude_l2 = any(sub in d_name for sub in ["人事", "行政", "總務", "採購", "財務", "會計", "設計", "課"])
                        
                        if is_l1 and not exclude_l2:
                            if d_name not in depts:
                                depts.append(d_name)
        except Exception:
            pass
        
        # 若資料庫抓取為空或異常，強制給予您規定的 5 大 L1 標準部門
        if not depts:
            depts = ["總經理室", "工程部", "管理部", "生產部", "倉庫管理"]

        if 'selected_dept' not in st.session_state:
            st.session_state['selected_dept'] = depts[0]

        # 側邊欄 L1 部門按鈕清單
        for d in depts:
            is_selected = (st.session_state['selected_dept'] == d)
            btn_type = "primary" if is_selected else "secondary"
            if st.button(f"🏛️ {d}", key=f"sidebar_dept_{d}", use_container_width=True, type=btn_type):
                st.session_state['selected_dept'] = d
                st.session_state['current_view'] = 'dashboard'
                st.session_state['active_feature_id'] = None
                st.rerun()

        st.divider()

        # ⚙️ 系統設定按鈕固定在側邊欄最下方
        if st.button("⚙️ 系統設定 (Cấu hình hệ thống)", use_container_width=True):
            st.session_state['current_view'] = 'dynamic_feature'
            st.session_state['active_feature_id'] = 'feat_it_menu'
            st.rerun()

    # ==========================================
    # 主畫面渲染區塊
    # ==========================================
    current_dept = st.session_state.get('selected_dept', '總經理室')

    # 1. 總經理室專屬路由
    if current_dept == '總經理室':
        try:
            from modules.executive import executive_dashboard
            executive_dashboard.render_executive_main(engine=db_engine, lang='zh')
        except Exception as e:
            st.error(f"載入總經理室模組發生錯誤: {e}")
        return

    # 2. 其他 L1 部門動態模組路由
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
        if '工程' in current_dept:
            mounted_feats_str = "feat_eng_overview,feat_site_log,feat_blueprint"
        elif '管理' in current_dept:
            mounted_feats_str = "feat_mgmt_supervisor,feat_announcements,feat_hr_employee,feat_hr_attendance,feat_hr_payroll,feat_ga,feat_fi"
        elif '生產' in current_dept:
            mounted_feats_str = "feat_prod_overview,feat_panel_build,feat_production_schedule"
        elif '倉庫' in current_dept:
            mounted_feats_str = "feat_warehouse_overview,feat_material,feat_barcode"
        else:
            mounted_feats_str = "feat_exec_announcements"

    feature_list = [f.strip() for f in mounted_feats_str.split(",") if f.strip()]

    feature_meta_map = {
        "feat_executive": {"name": "👑 總經理室戰情總覽", "desc": "全廠營運績效與決策總覽。"},
        "feat_lme_commodities": {"name": "📈 原料市場與外匯行情", "desc": "LME 銅價與即時匯率換算。"},
        "feat_stock_indices": {"name": "📈 全球股市指標追蹤", "desc": "追蹤台美中越股市行情。"},
        "feat_fx_rates": {"name": "💱 多幣別匯率換算引擎", "desc": "處理美元台幣越南盾換算。"},
        "feat_announcements": {"name": "📢 公司公告佈告欄管理", "desc": "管理部發布與管理公司公告。"},
        "feat_eng_overview": {"name": "🛠️ 工程部總覽 / 專案進度", "desc": "高低壓配電盤案場與進度追蹤。"},
        "feat_site_log": {"name": "📋 工程報告與工地巡檢日報", "desc": "填報工地日報與現場巡檢。"},
        "feat_blueprint": {"name": "📐 設計圖紙上傳與審查", "desc": "管理工程設計藍圖與審查（工程部專屬）。"},
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
                if st.button("進入模組 ➡️", key=f"enter_feat_{current_dept}_{feat_id}", use_container_width=True, type="primary"):
                    st.session_state['current_view'] = 'dynamic_feature'
                    st.session_state['active_feature_id'] = feat_id
                    st.rerun()
