# ==========================================
# 檔案路徑：modules/hr/attendance_leave.py
# 職責：管理部(人事) - 外勤打卡紀錄稽核、專案工時歸屬與薪資拋轉核准
# ==========================================

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from core import ui_theme
from modules.common.attendance_payroll_bridge import (
    approve_records_for_hr,
    ensure_hr_payroll_bridge_tables,
    fetch_hr_daily_labor,
    fetch_hr_field_clockins,
)


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    today_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date()
    first_day = today_vn.replace(day=1)

    txt = {
        "zh": {
            "title": "🕒 管理部（人事）－外勤打卡紀錄與專案工時核准",
            "sub": "同步接收工程部外勤 GPS 打卡與每日點工出勤，核准後直接拋轉薪資計算與專案人工成本。",
            "d_from": "查詢起始日",
            "d_to": "查詢結束日",
            "m1": "外勤工程打卡人次",
            "m2": "待人事核准筆數",
            "m3": "累計點工人天",
            "m4": "累計外包人天",
            "btn_ok": "✅ 核准區間內外勤打卡與點工紀錄（拋轉薪資計算）",
            "t1": "📍 外勤工程人員打卡紀錄明細",
            "t2": "👷 案場點工與外包出勤彙總（人工成本歸屬）",
        },
        "vi": {
            "title": "🕒 Hành Chính Nhân Sự - Duyệt Chấm Công Ngoài Công Trường & Giờ Công Dự Án",
            "sub": "Đồng bộ dữ liệu chấm công GPS và nhân công thời vụ từ bộ phận Kỹ thuật để tính lương và phân bổ chi phí dự án.",
            "d_from": "Từ Ngày",
            "d_to": "Đến Ngày",
            "m1": "Lượt Kỹ Sư Chấm Công",
            "m2": "Chờ Nhân Sự Duyệt",
            "m3": "Tổng Công Thời Vụ",
            "m4": "Tổng Công Thầu Phụ",
            "btn_ok": "✅ Phê Duyệt Chấm Công & Chuyển Sang Tính Lương",
            "t1": "📍 Chi Tiết Chấm Công Kỹ Sư Ngoài Công Trường",
            "t2": "👷 Tổng Hợp Thời Vụ & Thầu Phụ Theo Dự Án",
        },
        "en": {
            "title": "🕒 HR - Field Clock-In Audit & Project Workhour Approval",
            "sub": "Sync field GPS clock-ins and daily-wage headcount from Engineering for payroll and project labor costing.",
            "d_from": "From Date",
            "d_to": "To Date",
            "m1": "Field Clock-In Entries",
            "m2": "Pending HR Approval",
            "m3": "Daily-Wage Man-Days",
            "m4": "Subcon Man-Days",
            "btn_ok": "✅ Approve Period Records for Payroll",
            "t1": "📍 Field Engineer Clock-In Records",
            "t2": "👷 Daily-Wage & Subcon Summary by Project",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    ensure_hr_payroll_bridge_tables(engine)

    c_d1, c_d2 = st.columns(2)
    with c_d1:
        start_d = st.date_input(txt["d_from"], value=first_day, key="hr_att_sdate")
    with c_d2:
        end_d = st.date_input(txt["d_to"], value=today_vn, key="hr_att_edate")

    df_clk = fetch_hr_field_clockins(engine, tenant_id, start_d, end_d)
    df_lab = fetch_hr_daily_labor(engine, tenant_id, start_d, end_d)

    clk_total = len(df_clk)
    pending_clk = int((df_clk["hr_sync_status"] == "PENDING_HR").sum()) if not df_clk.empty else 0
    pending_lab = int((df_lab["hr_sync_status"] == "PENDING_HR").sum()) if not df_lab.empty else 0
    daily_mandays = int(df_lab["daily_wage_workers"].sum()) if not df_lab.empty else 0
    subcon_mandays = int(df_lab["subcon_workers"].sum()) if not df_lab.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(txt["m1"], f"{clk_total} 筆")
    k2.metric(txt["m2"], f"{pending_clk + pending_lab} 筆")
    k3.metric(txt["m3"], f"{daily_mandays} 人天")
    k4.metric(txt["m4"], f"{subcon_mandays} 人天")

    if st.button(txt["btn_ok"], type="primary", use_container_width=True):
        c_cnt, l_cnt = approve_records_for_hr(engine, tenant_id, start_d, end_d)
        st.success(f"✅ 已核准外勤打卡 {c_cnt} 筆、點工／外包出勤 {l_cnt} 筆，可至「自動化薪資計算」結算。")
        st.rerun()

    tab1, tab2 = st.tabs([txt["t1"], txt["t2"]])
    with tab1:
        if df_clk.empty:
            st.info("此日期區間尚無外勤工程人員打卡紀錄。")
        else:
            show_clk = df_clk.rename(
                columns={
                    "employee_id": "員工編號",
                    "employee_name": "工程人員",
                    "project_id": "歸屬專案",
                    "work_date": "打卡日期",
                    "clock_hm": "打卡時間",
                    "gps_address": "定位位置",
                    "hr_sync_status": "人事核准狀態",
                    "payroll_batch_id": "薪資批次",
                }
            ).drop(columns=["id"], errors="ignore")
            st.dataframe(show_clk, use_container_width=True, hide_index=True)

    with tab2:
        if df_lab.empty:
            st.info("此日期區間尚無點工／外包出勤紀錄。")
        else:
            show_lab = df_lab.rename(
                columns={
                    "work_date": "出勤日期",
                    "project_id": "歸屬專案",
                    "site_name": "工地／案場",
                    "subcon_id": "外包商編號",
                    "subcon_workers": "外包人數",
                    "daily_wage_workers": "點工人數",
                    "daily_wage_rate": "點工日薪(₫)",
                    "hr_sync_status": "人事核准狀態",
                    "payroll_batch_id": "薪資批次",
                }
            ).drop(columns=["id"], errors="ignore")
            st.dataframe(show_lab, use_container_width=True, hide_index=True)


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
