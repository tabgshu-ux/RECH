# ==========================================
# 檔案路徑：modules/executive/widgets/overview_panels.py
# 職責：總經理室首頁即時戰情區塊（原物料即時價格、即時通知、秘書行程安排）
# ==========================================

import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _load_secretary_schedules(engine, tenant_id: str) -> list[dict]:
    """讀取秘書行程安排（附安全降級預設資料，預留 schedule_id / project_id / approval_id）"""
    fallback = [
        {
            "schedule_id": "SCH-001",
            "time": "09:30",
            "title": "西寧廠二期配電盤擴建進度與材料成本覆核",
            "location": "總經理室 / 視訊",
            "owner": "秘書處・陳經理",
            "project_id": "PRJ-2026-01",
            "quote_id": "QT-2026-008",
            "approval_id": "APR-2026-019",
        },
        {
            "schedule_id": "SCH-002",
            "time": "14:00",
            "title": "LME 銅價高檔採購鎖價與供應商合約簽核",
            "location": "會議室 A",
            "owner": "秘書處・採購組",
            "project_id": "PRJ-2026-02",
            "quote_id": "QT-2026-011",
            "approval_id": "APR-2026-024",
        },
        {
            "schedule_id": "SCH-003",
            "time": "16:30",
            "title": "海防廠案場驗收報告與越籍幹部排班確認",
            "location": "總經理室",
            "owner": "秘書處・行政組",
            "project_id": "PRJ-2026-03",
            "quote_id": None,
            "approval_id": "APR-2026-027",
        },
    ]
    if not engine:
        return fallback
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT schedule_id, schedule_time, title, location, owner, project_id, quote_id, approval_id
                    FROM exec_secretary_schedules
                    WHERE tenant_id = :tid
                    ORDER BY schedule_time ASC, id ASC
                    LIMIT 10
                """),
                {"tid": tenant_id},
            ).fetchall()
            if rows:
                return [r._asdict() for r in rows]
    except Exception:
        pass
    return fallback


def render_executive_home_panels(engine, tenant_id: str, lang: str = "zh"):
    code = ui_theme.norm_lang(lang)

    titles = {
        "zh": {
            "banner": "📢 全廠即時通知",
            "ann_1": "【總經理室／管理部通知】西寧與海防廠區施工安全巡檢與斷電檢點持續落實，異常請即時回報。",
            "ann_2": "【採購與財務提醒】LME 銅價處於高檔區間，大額工程估價與採購單請依權限送交簽核中心。",
            "kpi_ar": "應收帳款總額 (Total AR)",
            "kpi_ap": "應付帳款成本 (Total AP)",
            "kpi_profit": "本月毛利與稅後淨利",
            "kpi_copper": "銅價即時行情 (LME)",
            "raw_title": "🪙 原物料即時價格與匯率行情",
            "col_mat": "原物料 / 匯率項目",
            "col_price": "即時價格",
            "col_chg": "漲跌 / 狀態",
            "col_note": "決策提示",
            "sec_title": "🗓️ 秘書行程安排",
            "sec_empty": "今日尚無秘書排定行程。",
        },
        "vi": {
            "banner": "📢 Thông Báo Khẩn Toàn Công Ty",
            "ann_1": "[VP TGĐ / Hành Chính] Tăng cường kiểm tra an toàn thi công và ngắt điện tại nhà máy Tây Ninh & Hải Phòng.",
            "ann_2": "[Mua Hàng / Kế Toán] Giá đồng LME ở vùng cao, báo giá dự án và đơn mua hàng lớn cần trình ký duyệt.",
            "kpi_ar": "Tổng Phải Thu (Total AR)",
            "kpi_ap": "Tổng Phải Trả (Total AP)",
            "kpi_profit": "Lợi Nhuận Gộp & Ròng Tháng",
            "kpi_copper": "Giá Đồng LME Tức Thời",
            "raw_title": "🪙 Giá Nguyên Vật Liệu & Tỷ Giá Tức Thời",
            "col_mat": "Hạng Mục / Tỷ Giá",
            "col_price": "Giá Hiện Tại",
            "col_chg": "Biến Động",
            "col_note": "Ghi Chú Điều Hành",
            "sec_title": "🗓️ Lịch Làm Việc Do Thư Ký Sắp Xếp",
            "sec_empty": "Hôm nay chưa có lịch hẹn nào.",
        },
        "en": {
            "banner": "📢 Live Company Announcements",
            "ann_1": "[GM / Admin Notice] Maintain safety inspections and power checks across Tay Ninh and Hai Phong sites.",
            "ann_2": "[Procurement / Finance] LME copper is elevated; route major quotes and POs through the Approval Center.",
            "kpi_ar": "Total Accounts Receivable (AR)",
            "kpi_ap": "Total Accounts Payable (AP)",
            "kpi_profit": "Monthly Gross & Net Profit",
            "kpi_copper": "Live LME Copper Price",
            "raw_title": "🪙 Live Raw Material Prices & FX Rates",
            "col_mat": "Material / FX Item",
            "col_price": "Live Price",
            "col_chg": "Change / Status",
            "col_note": "Action Note",
            "sec_title": "🗓️ Secretary Schedule",
            "sec_empty": "No secretary appointments scheduled today.",
        },
    }[code]

    # 1. 即時通知
    st.markdown(f"#### {titles['banner']}")
    n1, n2 = st.columns(2)
    with n1:
        st.info(titles["ann_1"])
    with n2:
        st.warning(titles["ann_2"])

    # 2. 核心營運 KPI 總覽
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(titles["kpi_ar"], "141,630,132,003 ₫", "+4.2%")
    with k2:
        st.metric(titles["kpi_ap"], "45,200,000,000 ₫", "-1.8%")
    with k3:
        st.metric(titles["kpi_profit"], "27,600,000,000 ₫", "+6.5%")
    with k4:
        st.metric(titles["kpi_copper"], "$14,400 USD/噸", "+1.8%")

    st.divider()

    # 3. 原物料即時價格
    st.markdown(f"#### {titles['raw_title']}")
    raw_df = pd.DataFrame([
        {
            titles["col_mat"]: "LME 導電銅價 (Copper Grade A)",
            titles["col_price"]: "$14,400 USD / 噸",
            titles["col_chg"]: "🟢 +1.8%",
            titles["col_note"]: "高檔震盪，大型配電盤案場建議鎖定成本",
        },
        {
            titles["col_mat"]: "工業導電鋁型材 (Aluminum Profiles)",
            titles["col_price"]: "$3,149 USD / 噸",
            titles["col_chg"]: "🟡 -0.5%",
            titles["col_note"]: "價格平穩，依案場排程叫料",
        },
        {
            titles["col_mat"]: "美元兌越南盾匯率 (USD/VND)",
            titles["col_price"]: "25,450 ₫",
            titles["col_chg"]: "🟢 穩定",
            titles["col_note"]: "留意進口料款結匯時點",
        },
        {
            titles["col_mat"]: "新台幣兌越南盾匯率 (TWD/VND)",
            titles["col_price"]: "795 ₫",
            titles["col_chg"]: "🟢 +0.2%",
            titles["col_note"]: "母子公司資金調度正常",
        },
    ])
    st.dataframe(raw_df, use_container_width=True, hide_index=True)

    st.divider()

    # 4. 即時通知下方直接顯示「秘書行程安排」
    st.markdown(f"#### {titles['sec_title']}")
    schedules = _load_secretary_schedules(engine, tenant_id)
    if not schedules:
        st.info(titles["sec_empty"])
    else:
        for item in schedules:
            with st.container(border=True):
                c_time, c_info = st.columns([1.2, 4.8])
                with c_time:
                    st.markdown(f"⏰ **{item.get('schedule_time') or item.get('time') or '--:--'}**")
                    st.caption(item.get("location") or "")
                with c_info:
                    st.markdown(f"**{item.get('title') or ''}**")
                    ref_tags = []
                    if item.get("owner"):
                        ref_tags.append(str(item["owner"]))
                    if item.get("project_id"):
                        ref_tags.append(f"專案: {item['project_id']}")
                    if item.get("quote_id"):
                        ref_tags.append(f"估價: {item['quote_id']}")
                    if item.get("approval_id"):
                        ref_tags.append(f"簽核: {item['approval_id']}")
                    st.caption(" ｜ ".join(ref_tags))
