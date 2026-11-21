# ==========================================
# 檔案路徑：modules/management/overview.py
# 職責：管理部總覽（彙整財務應收/應付、人事薪資與缺額/開價/應徵連結、總務採購/設備維修/宿舍開銷）
# ==========================================

import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def _load_finance_summary(engine, tenant_id: str) -> tuple[float, float, pd.DataFrame]:
    """讀取財務應收/應付與近期帳務明細（含安全降級）"""
    fallback_rows = [
        {
            "doc_no": "AR-202611-01",
            "project_id": "PRJ-2026-01",
            "category": "應收帳款 (AR)",
            "counterparty": "西寧廠二期工程業主",
            "summary": "配電盤設備第一期估驗請款",
            "amount_vnd": 380000000.0,
            "status": "UNPAID_AR",
        },
        {
            "doc_no": "AP-202611-01",
            "project_id": "PRJ-2026-01",
            "category": "應付帳款 (AP)",
            "counterparty": "Công Ty TNHH Thiết Bị Điện",
            "summary": "主斷路器與銅排採購應付",
            "amount_vnd": 145000000.0,
            "status": "UNPAID_AP",
        },
        {
            "doc_no": "AP-202611-02",
            "project_id": "PRJ-2026-02",
            "category": "應付帳款 (AP)",
            "counterparty": "Công Ty TNHH Cơ Điện Tây Ninh",
            "summary": "電纜橋架外包估驗款項",
            "amount_vnd": 45000000.0,
            "status": "PENDING_PAY",
        },
    ]
    if not engine:
        df = pd.DataFrame(fallback_rows)
        return 380000000.0, 190000000.0, df

    try:
        with engine.connect() as conn:
            has_tbl = conn.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'fin_ledger_entries'
                    )
                """)
            ).scalar()
            if has_tbl:
                rows = conn.execute(
                    text("""
                        SELECT doc_no,
                               COALESCE(project_id, '-') AS project_id,
                               category,
                               COALESCE(counterparty, '-') AS counterparty,
                               COALESCE(summary, '-') AS summary,
                               COALESCE(amount_vnd, 0) AS amount_vnd,
                               COALESCE(status, 'OPEN') AS status
                        FROM fin_ledger_entries
                        WHERE tenant_id = :tid
                        ORDER BY id DESC LIMIT 30
                    """),
                    {"tid": tenant_id},
                ).fetchall()
                if rows:
                    df = pd.DataFrame([r._asdict() for r in rows])
                    ar_sum = float(df[df["category"].str.contains("AR|應收", case=False, na=False)]["amount_vnd"].sum())
                    ap_sum = float(df[df["category"].str.contains("AP|應付", case=False, na=False)]["amount_vnd"].sum())
                    return ar_sum, ap_sum, df
    except Exception:
        pass

    df = pd.DataFrame(fallback_rows)
    return 380000000.0, 190000000.0, df


def _load_hr_payroll_and_vacancies(engine, tenant_id: str) -> tuple[float, pd.DataFrame]:
    """讀取人事薪資金額與人員缺額、開價薪資、應徵網址（串接臨時工/點工待結算與招募缺額）"""
    worker_pending_vnd = 0.0
    if engine:
        try:
            with engine.connect() as conn:
                val = conn.execute(
                    text("""
                        SELECT COALESCE(SUM(total_amount_vnd), 0)
                        FROM hr_daily_worker_logs
                        WHERE tenant_id = :tid AND payroll_status = 'PENDING_PAYROLL'
                    """),
                    {"tid": tenant_id},
                ).scalar()
                worker_pending_vnd = float(val or 0)
        except Exception:
            worker_pending_vnd = 0.0

    base_monthly_payroll = 245000000.0
    total_hr_payroll = base_monthly_payroll + worker_pending_vnd

    vacancies = [
        {
            "vacancy_id": "VAC-ENG-01",
            "dept_name": "工程部／現場組",
            "role_title": "水電／機電工程師 (Kỹ sư Cơ điện)",
            "openings": 2,
            "offered_salary": "18.000.000 - 25.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/mep-engineer",
            "status": "招募中",
        },
        {
            "vacancy_id": "VAC-PROD-02",
            "dept_name": "生產部／配盤組",
            "role_title": "配電盤組裝與配線技師 (Thợ lắp tủ điện)",
            "openings": 3,
            "offered_salary": "10.000.000 - 15.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/panel-wirer",
            "status": "招募中",
        },
        {
            "vacancy_id": "VAC-GA-01",
            "dept_name": "管理部／總務採購",
            "role_title": "採購與後勤專員 (Nhân viên Mua hàng)",
            "openings": 1,
            "offered_salary": "12.000.000 - 16.000.000 ₫ / 月",
            "apply_url": "https://careers.reetech-industrial.example.com/jobs/procurement",
            "status": "招募中",
        },
    ]

    if engine:
        try:
            with engine.connect() as conn:
                has_vac = conn.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables
                            WHERE table_schema = 'public' AND table_name = 'hr_job_vacancies'
                        )
                    """)
                ).scalar()
                if has_vac:
                    rows = conn.execute(
                        text("""
                            SELECT vacancy_id, dept_name, role_title, openings,
                                   offered_salary, apply_url, status
                            FROM hr_job_vacancies
                            WHERE tenant_id = :tid
                            ORDER BY id DESC
                        """),
                        {"tid": tenant_id},
                    ).fetchall()
                    if rows:
                        return total_hr_payroll, pd.DataFrame([r._asdict() for r in rows])
        except Exception:
            pass

    return total_hr_payroll, pd.DataFrame(vacancies)


def _load_ga_expenses(engine, tenant_id: str) -> tuple[float, float, float, pd.DataFrame]:
    """讀取總務採購項目與金額、設備維修項目與金額、宿舍開銷金額"""
    items = [
        {
            "item_id": "GA-PUR-01",
            "expense_type": "總務採購",
            "item_name": "廠區辦公耗材、安全帽與勞保防護用品",
            "amount_vnd": 28500000.0,
            "ref_no": "PR-202611-04",
            "status": "已核准",
        },
        {
            "item_id": "GA-PUR-02",
            "expense_type": "總務採購",
            "item_name": "飲用水、清潔用品與工地茶水補給",
            "amount_vnd": 9200000.0,
            "ref_no": "PR-202611-09",
            "status": "已核准",
        },
        {
            "item_id": "GA-MNT-01",
            "expense_type": "設備維修",
            "item_name": "折床液壓系統保養與空壓機管路檢修",
            "amount_vnd": 22000000.0,
            "ref_no": "MNT-202611-02",
            "status": "處理中",
        },
        {
            "item_id": "GA-MNT-02",
            "expense_type": "設備維修",
            "item_name": "公務車 61C-452.18 輪胎更換與底盤定位",
            "amount_vnd": 8400000.0,
            "ref_no": "MNT-202611-05",
            "status": "已完成",
        },
        {
            "item_id": "GA-DRM-01",
            "expense_type": "宿舍開銷",
            "item_name": "西寧員工宿舍租金、水電費與瓦斯網路費",
            "amount_vnd": 36000000.0,
            "ref_no": "DORM-202611-01",
            "status": "本月帳單",
        },
    ]

    if engine:
        try:
            with engine.connect() as conn:
                has_ga = conn.execute(
                    text("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables
                            WHERE table_schema = 'public' AND table_name = 'ga_expense_items'
                        )
                    """)
                ).scalar()
                if has_ga:
                    rows = conn.execute(
                        text("""
                            SELECT item_id, expense_type, item_name,
                                   COALESCE(amount_vnd, 0) AS amount_vnd,
                                   COALESCE(ref_no, '-') AS ref_no,
                                   COALESCE(status, 'OPEN') AS status
                            FROM ga_expense_items
                            WHERE tenant_id = :tid
                            ORDER BY id DESC LIMIT 50
                        """),
                        {"tid": tenant_id},
                    ).fetchall()
                    if rows:
                        df = pd.DataFrame([r._asdict() for r in rows])
                        pur_s = float(df[df["expense_type"].str.contains("採購", na=False)]["amount_vnd"].sum())
                        mnt_s = float(df[df["expense_type"].str.contains("維修", na=False)]["amount_vnd"].sum())
                        drm_s = float(df[df["expense_type"].str.contains("宿舍", na=False)]["amount_vnd"].sum())
                        return pur_s, mnt_s, drm_s, df
        except Exception:
            pass

    df = pd.DataFrame(items)
    pur_s = float(df[df["expense_type"] == "總務採購"]["amount_vnd"].sum())
    mnt_s = float(df[df["expense_type"] == "設備維修"]["amount_vnd"].sum())
    drm_s = float(df[df["expense_type"] == "宿舍開銷"]["amount_vnd"].sum())
    return pur_s, mnt_s, drm_s, df


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")

    st.markdown("### 🏢 管理部總覽（財務帳務／人事薪資與招募／總務採購·維修·宿舍）")
    st.caption("統籌管理部三大核心區塊：財務應收應付、人事薪資與人員缺額、總務採購與設備維修及宿舍開銷。")

    ar_vnd, ap_vnd, df_fin = _load_finance_summary(engine, tenant_id)
    hr_payroll_vnd, df_vac = _load_hr_payroll_and_vacancies(engine, tenant_id)
    ga_pur_vnd, ga_mnt_vnd, ga_drm_vnd, df_ga = _load_ga_expenses(engine, tenant_id)
    ga_total_vnd = ga_pur_vnd + ga_mnt_vnd + ga_drm_vnd

    # 頂部四大核心總表指標
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💳 財務應收帳款 (AR)", f"{_fmt_vnd(ar_vnd)} ₫")
    k2.metric("🧾 財務應付帳款 (AP)", f"{_fmt_vnd(ap_vnd)} ₫")
    k3.metric("💵 人事薪資金額", f"{_fmt_vnd(hr_payroll_vnd)} ₫")
    k4.metric("🏗️ 總務總開銷（採購/維修/宿舍）", f"{_fmt_vnd(ga_total_vnd)} ₫")

    st.divider()

    # 1. 財務/會計：應收/應付與現在帳務資料
    st.markdown("#### 💳 一、財務／會計：應收／應付與帳務明細")
    f_m1, f_m2, f_m3 = st.columns(3)
    f_m1.metric("應收帳款合計 (AR)", f"{_fmt_vnd(ar_vnd)} ₫")
    f_m2.metric("應付帳款合計 (AP)", f"{_fmt_vnd(ap_vnd)} ₫")
    f_m3.metric("應收減應付淨額", f"{_fmt_vnd(ar_vnd - ap_vnd)} ₫")

    if not df_fin.empty:
        disp_fin = df_fin.copy()
        disp_fin["金額(₫)"] = disp_fin["amount_vnd"].apply(_fmt_vnd)
        disp_fin = disp_fin.rename(columns={
            "doc_no": "單據編號",
            "project_id": "專案",
            "category": "帳務類別",
            "counterparty": "往來對象",
            "summary": "帳務摘要",
            "status": "狀態",
        })
        st.dataframe(
            disp_fin[["單據編號", "專案", "帳務類別", "往來對象", "帳務摘要", "金額(₫)", "狀態"]],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # 2. 行政/人事：薪資金額、人員缺額、開價薪資與應徵網址
    st.markdown("#### 👥 二、行政／人事：薪資金額、人員缺額與招募資訊")
    h_m1, h_m2, h_m3 = st.columns(3)
    h_m1.metric("本月／待結算薪資總金額", f"{_fmt_vnd(hr_payroll_vnd)} ₫")
    h_m2.metric("招募職缺數", f"{len(df_vac)} 項")
    h_m3.metric("徵才缺額總人數", f"{int(df_vac['openings'].sum()) if not df_vac.empty else 0} 人")

    if not df_vac.empty:
        disp_vac = df_vac.rename(columns={
            "vacancy_id": "職缺編號",
            "dept_name": "需求部門",
            "role_title": "職稱／職務",
            "openings": "缺額人數",
            "offered_salary": "開價薪資",
            "apply_url": "應徵網址",
            "status": "狀態",
        })
        st.dataframe(
            disp_vac,
            use_container_width=True,
            hide_index=True,
            column_config={
                "應徵網址": st.column_config.LinkColumn("應徵網址", display_text="開啟應徵頁面"),
            },
        )

    st.divider()

    # 3. 總務/採購：採購項目與金額、設備維修項目與金額、宿舍開銷金額
    st.markdown("#### 🛍️ 三、總務／採購：採購項目、設備維修與宿舍開銷")
    g_m1, g_m2, g_m3 = st.columns(3)
    g_m1.metric("總務採購金額", f"{_fmt_vnd(ga_pur_vnd)} ₫")
    g_m2.metric("設備維修金額", f"{_fmt_vnd(ga_mnt_vnd)} ₫")
    g_m3.metric("宿舍開銷金額", f"{_fmt_vnd(ga_drm_vnd)} ₫")

    if not df_ga.empty:
        disp_ga = df_ga.copy()
        disp_ga["金額(₫)"] = disp_ga["amount_vnd"].apply(_fmt_vnd)
        disp_ga = disp_ga.rename(columns={
            "item_id": "項目編號",
            "expense_type": "費用類別",
            "item_name": "項目與說明",
            "ref_no": "關聯單號",
            "status": "狀態",
        })
        st.dataframe(
            disp_ga[["項目編號", "費用類別", "項目與說明", "金額(₫)", "關聯單號", "狀態"]],
            use_container_width=True,
            hide_index=True,
        )


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
