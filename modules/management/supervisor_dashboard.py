# ==========================================
# 檔案路徑：modules/management/supervisor_dashboard.py
# 職責：管理部主管綜合戰情儀表板（含請假早退名單、當月採購金額、車輛維修保養費用統合）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import datetime

def render(engine=None, lang="繁體中文", **kwargs):
    st.subheader("📊 管理部主管綜合戰情儀表板 (Management Supervisor Dashboard)")
    st.caption("統合管理部各課室關鍵數據：包含出勤異常（請假、早退）人員名單、當月採購總花費、車輛維修保養費用與內控合規指標。")
    st.markdown("---")

    # 頂部三大核心 KPI 總覽卡片
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        with st.container(border=True):
            st.metric("👥 本月請假/早退總人次", "14 人次", delta="-2 人", delta_color="inverse")
    with col_kpi2:
        with st.container(border=True):
            st.metric("🛒 當月採購總金額 (VND)", "185,450,000₫", delta="+12.5%")
    with col_kpi3:
        with st.container(border=True):
            st.metric("🚗 車輛維修保養總花費", "14,200,000₫", delta="-5.2%", delta_color="inverse")
    with col_kpi4:
        with st.container(border=True):
            st.metric("🏢 宿舍與後勤滿意度", "94.5%", delta="+2.1%")

    st.markdown("<br>", unsafe_allow_html=True)

    # 分頁檢視詳細資料
    tab_leave, tab_procurement, tab_vehicle = st.tabs([
        "📋 人事考勤：請假與早退人員名單", 
        "💰 總務採購：當月採購金額與明細", 
        "🔧 車輛管理：維修保養費用統合"
    ])

    # 1. 請假與早退人員名單
    with tab_leave:
        st.markdown("##### 📌 本月請假、早退與出勤異常即時名單")
        st.caption("資料來源：人事行政課出勤打卡與請假系統即時同步。")

        leave_df = pd.DataFrame([
            {"日期": "2026-11-06", "工號": "REC-0102", "姓名": "Nguyễn Văn A", "部門": "生產部-板金組", "假別/狀況": "事假 (全天)", "時數": "8 小時", "審核狀態": "已核准 🟢"},
            {"日期": "2026-11-06", "工號": "REC-0145", "姓名": "Trần Thị B", "部門": "管理部-總務課", "假別/狀況": "早退 (下午)", "時數": "3.5 小時", "審核狀態": "已核准 🟢"},
            {"日期": "2026-11-05", "工號": "REC-0210", "姓名": "Lê Văn C", "部門": "工程部-案場組", "假別/狀況": "病假 (半天)", "時數": "4 小時", "審核狀態": "主管審核中 🟡"},
            {"日期": "2026-11-04", "工號": "REC-0089", "姓名": "范文雄", "部門": "生產部-配盤組", "假別/狀況": "事假 (全天)", "時數": "8 小時", "審核狀態": "已核准 🟢"},
        ])
        st.dataframe(leave_df, use_container_width=True)
        
        col_dl1, col_dl2 = st.columns([1, 4])
        with col_dl1:
            if st.button("📥 匯出本月考勤異常報表", use_container_width=True):
                st.success("✅ 考勤異常報表已成功匯出至 Excel！")

    # 2. 當月採購金額花費
    with tab_procurement:
        st.markdown("##### 🛒 管理部/總務採購課：當月採購金額與明細統計")
        st.caption("彙整西寧廠與海防廠各項請購案、發包與應付帳款 (AP) 立帳金額。")

        proc_df = pd.DataFrame([
            {"採購單號": "PO-202611-001", "日期": "2026-11-02", "供應商名稱": "Công ty TNHH Thép Miền Nam", "採購類別": "生產原料 (鋼板/銅排)", "金額 (VND)": "95,000,000₫", "狀態": "已付款"},
            {"採購單號": "PO-202611-002", "日期": "2026-11-04", "供應商名稱": "Nhà hàng Suối Tiên (伙食承包)", "採購類別": "員工伙食與宿舍開銷", "金額 (VND)": "45,000,000₫", "狀態": "請款審核中"},
            {"採購單號": "PO-202611-003", "日期": "2026-11-05", "供應商名稱": "Thiết bị Điện Sài Gòn", "採購類別": "工安防護具與五金耗材", "金額 (VND)": "28,450,000₫", "狀態": "已立帳 (AP)"},
            {"採購單號": "PO-202611-004", "日期": "2026-11-06", "供應商名稱": "Văn phòng phẩm An Tâm", "採購類別": "辦公文具與耗材", "金額 (VND)": "17,000,000₫", "狀態": "已付款"},
        ])
        st.dataframe(proc_df, use_container_width=True)

        st.info("💡 **採購內控提示**：當月總採購金額已達預算警戒線之 72%，大額採購請確保已完成三家比價與電子簽核流程。")

    # 3. 車輛維修保養金額
    with tab_vehicle:
        st.markdown("##### 🔧 總務後勤：車輛維修保養金額與明細統合")
        st.caption("追蹤廠區輕型貨車、公務車之定期保養、零件更換與保險理賠支出。")

        veh_df = pd.DataFrame([
            {"車牌號碼": "61C-889.21 (輕型貨車)", "保養日期": "2026-11-01", "保養廠名稱": "Gara Ô tô Tây Ninh", "維修保養項目": "更換輪胎 2 條、煞車皮與機油", "費用 (VND)": "6,800,000₫", "經辦人": "Nguyễn Văn D"},
            {"車牌號碼": "51H-432.10 (公務車)", "保養日期": "2026-11-03", "保養廠名稱": "Toyota Sài Gòn Service", "維修保養項目": "定期 5 萬公里大保養、冷氣濾網清洗", "費用 (VND)": "4,500,000₫", "經辦人": "Trần Văn E"},
            {"車牌號碼": "61C-125.88 (工程貨車)", "保養日期": "2026-11-05", "保養廠名稱": "Gara Minh Tâm", "維修保養項目": "PTO 油壓控制桿漏油修復與保養", "費用 (VND)": "2,900,000₫", "經辦人": "Phạm Văn F"},
        ])
        st.dataframe(veh_df, use_container_width=True)

        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.metric("🚚 輕型貨車維修佔比", "68.3% (9,700,000₫)")
        with col_v2:
            st.metric("🚗 公務小客車佔比", "31.7% (4,500,000₫)")

def show(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
