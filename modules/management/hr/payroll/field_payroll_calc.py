# ==========================================
# 檔案路徑：modules/management/hr/payroll/field_payroll_calc.py
# 職責：管理部(人事) - 薪資子資料夾內之自動化薪資與點工結算（串接外勤打卡、津貼、社保與專案歸屬）
# ==========================================

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme
from modules.common.attendance_payroll_bridge import (
    ensure_hr_payroll_bridge_tables,
    fetch_hr_daily_labor,
    fetch_hr_field_clockins,
)


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def render(engine=None, lang="zh", **kwargs):
    code = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")
    user_name = st.session_state.get("user_name", "HR_Admin")
    now_vn = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    default_ym = now_vn.strftime("%Y-%m")

    txt = {
        "zh": {
            "title": "💵 自動化薪資計算與點工結算",
            "sub": "自動彙整外勤工程人員出勤天數（底薪＋工地津貼－社保）與案場點工工資，結算後鎖定考勤批次。",
            "ym": "結算月份 (YYYY-MM)",
            "base_sal": "正職月標準底薪 (₫)",
            "allowance": "外勤工地津貼／日 (₫)",
            "bhxh_pct": "員工社保扣繳比例 (%)",
            "settle_btn": "🔒 確認結算寫入薪資單並鎖定考勤紀錄",
            "t1": "1️⃣ 本期薪資與點工試算表",
            "t2": "2️⃣ 已結算薪資批次紀錄",
        },
        "vi": {
            "title": "💵 Tính Lương Tự Động & Thanh Toán Thời Vụ",
            "sub": "Tổng hợp ngày công kỹ sư ngoài công trường và công thời vụ theo dự án, khóa dữ liệu sau khi chốt lương.",
            "ym": "Kỳ Lương (YYYY-MM)",
            "base_sal": "Lương Cơ Bản Chuẩn / Tháng (₫)",
            "allowance": "Phụ Cấp Công Trường / Ngày (₫)",
            "bhxh_pct": "Tỷ Lệ Trích BHXH Nhân Viên (%)",
            "settle_btn": "🔒 Chốt Bảng Lương & Khóa Dữ Liệu Chấm Công",
            "t1": "1️⃣ Bảng Tính Lương & Thời Vụ Kỳ Này",
            "t2": "2️⃣ Lịch Sử Đợt Đã Chốt Lương",
        },
        "en": {
            "title": "💵 Automated Payroll & Daily-Wage Settlement",
            "sub": "Aggregate field engineer attendance and site daily-wage labor, locking batch records after settlement.",
            "ym": "Payroll Month (YYYY-MM)",
            "base_sal": "Standard Monthly Base Salary (₫)",
            "allowance": "Site Allowance / Day (₫)",
            "bhxh_pct": "Employee Social Insurance (%)",
            "settle_btn": "🔒 Finalize Payroll & Lock Attendance Batch",
            "t1": "1️⃣ Current Period Payroll Worksheet",
            "t2": "2️⃣ Finalized Payroll Batches",
        },
    }[code]

    st.markdown(f"### {txt['title']}")
    st.caption(txt["sub"])
    ensure_hr_payroll_bridge_tables(engine)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        period_ym = st.text_input(txt["ym"], value=default_ym)
    with c2:
        std_base_salary = st.number_input(txt["base_sal"], min_value=0, value=14000000, step=500000)
    with c3:
        site_allow_day = st.number_input(txt["allowance"], min_value=0, value=120000, step=10000)
    with c4:
        bhxh_rate = st.number_input(txt["bhxh_pct"], min_value=0.0, max_value=25.0, value=10.5, step=0.5)

    try:
        yr, mo = [int(x) for x in period_ym.strip().split("-")]
        start_d = datetime(yr, mo, 1).date()
        end_d = (datetime(yr + 1, 1, 1) if mo == 12 else datetime(yr, mo + 1, 1)).date() - timedelta(days=1)
    except Exception:
        start_d = now_vn.date().replace(day=1)
        end_d = now_vn.date()

    tab1, tab2 = st.tabs([txt["t1"], txt["t2"]])

    with tab1:
        df_clk = fetch_hr_field_clockins(engine, tenant_id, start_d, end_d)
        df_lab = fetch_hr_daily_labor(engine, tenant_id, start_d, end_d)

        payroll_rows = []

        if not df_clk.empty:
            approved_clk = df_clk[df_clk["hr_sync_status"] == "HR_APPROVED"]
            src_clk = approved_clk if not approved_clk.empty else df_clk
            for emp_name, grp in src_clk.groupby("employee_name"):
                work_days = int(grp["work_date"].nunique())
                main_proj = str(grp["project_id"].mode().iloc[0]) if not grp["project_id"].empty else "未指定專案"
                emp_id = str(grp["employee_id"].iloc[0]) if "employee_id" in grp else "-"
                prorated_base = round((float(std_base_salary) / 26.0) * work_days)
                allow_amt = round(float(site_allow_day) * work_days)
                ins_amt = round(float(std_base_salary) * (float(bhxh_rate) / 100.0))
                net_amt = max(prorated_base + allow_amt - ins_amt, 0)
                payroll_rows.append({
                    "人員／工班": emp_name,
                    "員工編號": emp_id,
                    "類別": "正職外勤工程",
                    "主要歸屬專案": main_proj,
                    "出勤人天": work_days,
                    "應發底薪／工資": prorated_base,
                    "工地津貼": allow_amt,
                    "社保扣繳": ins_amt,
                    "實發／應付淨額": net_amt,
                })

        if not df_lab.empty:
            approved_lab = df_lab[df_lab["hr_sync_status"] == "HR_APPROVED"]
            src_lab = approved_lab if not approved_lab.empty else df_lab
            for (proj_id, site_name), grp in src_lab.groupby(["project_id", "site_name"]):
                mandays = int(grp["daily_wage_workers"].sum())
                if mandays <= 0:
                    continue
                avg_rate = float(grp["daily_wage_rate"].mean() or 450000)
                wage_total = round(mandays * avg_rate)
                payroll_rows.append({
                    "人員／工班": f"{site_name}（點工彙總）",
                    "員工編號": "DAILY-WAGE",
                    "類別": "現場點工",
                    "主要歸屬專案": proj_id,
                    "出勤人天": mandays,
                    "應發底薪／工資": wage_total,
                    "工地津貼": 0,
                    "社保扣繳": 0,
                    "實發／應付淨額": wage_total,
                })

        if not payroll_rows:
            st.info("本期尚無外勤打卡或點工出勤紀錄可供計算；請先至考勤功能核准資料。")
        else:
            df_pay = pd.DataFrame(payroll_rows)
            tot_net = float(df_pay["實發／應付淨額"].sum())
            tot_mandays = int(df_pay["出勤人天"].sum())

            m1, m2, m3 = st.columns(3)
            m1.metric("計薪項目數", f"{len(df_pay)} 筆")
            m2.metric("本期總計人天", f"{tot_mandays} 人天")
            m3.metric("本期薪資與點工總額", f"{_fmt_vnd(tot_net)} ₫")

            disp_pay = df_pay.copy()
            for col in ["應發底薪／工資", "工地津貼", "社保扣繳", "實發／應付淨額"]:
                disp_pay[col] = disp_pay[col].apply(_fmt_vnd)
            st.dataframe(disp_pay, use_container_width=True, hide_index=True)

            if st.button(txt["settle_btn"], type="primary", use_container_width=True):
                if not engine:
                    st.error("❌ 尚未連線資料庫。")
                else:
                    batch_id = f"PAY-{period_ym.replace('-', '')}-{now_vn.strftime('%H%M%S')}"
                    try:
                        with engine.begin() as conn:
                            for r in payroll_rows:
                                conn.execute(
                                    text("""
                                        INSERT INTO hr_payroll_settlements (
                                            tenant_id, payroll_batch_id, period_ym, employee_id,
                                            employee_name, worker_category, project_id, work_days,
                                            base_or_daily_pay, site_allowance, social_ins_deduct,
                                            net_pay, status, settled_by
                                        )
                                        VALUES (
                                            :tid, :bid, :ym, :eid,
                                            :ename, :wcat, :pid, :wdays,
                                            :bpay, :allow, :ins,
                                            :net, 'LOCKED', :sby
                                        )
                                    """),
                                    {
                                        "tid": tenant_id,
                                        "bid": batch_id,
                                        "ym": period_ym.strip(),
                                        "eid": r["員工編號"],
                                        "ename": r["人員／工班"],
                                        "wcat": "DAILY_WAGE" if r["類別"] == "現場點工" else "FIELD_ENGINEER",
                                        "pid": r["主要歸屬專案"],
                                        "wdays": r["出勤人天"],
                                        "bpay": r["應發底薪／工資"],
                                        "allow": r["工地津貼"],
                                        "ins": r["社保扣繳"],
                                        "net": r["實發／應付淨額"],
                                        "sby": user_name,
                                    },
                                )
                            conn.execute(
                                text("""
                                    UPDATE eng_field_clockins
                                    SET hr_sync_status = 'PAYROLL_LOCKED', payroll_batch_id = :bid
                                    WHERE tenant_id = :tid
                                      AND DATE(clock_time AT TIME ZONE 'Asia/Ho_Chi_Minh') BETWEEN :sdate AND :edate
                                      AND payroll_batch_id IS NULL
                                """),
                                {"bid": batch_id, "tid": tenant_id, "sdate": start_d, "edate": end_d},
                            )
                            conn.execute(
                                text("""
                                    UPDATE eng_daily_labor_headcount
                                    SET hr_sync_status = 'PAYROLL_LOCKED', payroll_batch_id = :bid
                                    WHERE tenant_id = :tid
                                      AND work_date BETWEEN :sdate AND :edate
                                      AND payroll_batch_id IS NULL
                                """),
                                {"bid": batch_id, "tid": tenant_id, "sdate": start_d, "edate": end_d},
                            )
                        st.success(f"✅ 已完成薪資結算（批次號：`{batch_id}`），原始外勤打卡與點工紀錄已鎖定防呆。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 薪資結算寫入失敗：{e}")

    with tab2:
        if not engine:
            st.info("尚無已結算薪資紀錄。")
            return
        try:
            with engine.connect() as conn:
                rows = conn.execute(
                    text("""
                        SELECT payroll_batch_id AS "薪資批次", period_ym AS "月份",
                               employee_name AS "人員／工班", worker_category AS "類別",
                               project_id AS "歸屬專案", work_days AS "人天",
                               net_pay, status AS "狀態", settled_by AS "結算人"
                        FROM hr_payroll_settlements
                        WHERE tenant_id = :tid
                        ORDER BY id DESC
                        LIMIT 50
                    """),
                    {"tid": tenant_id},
                ).fetchall()
                if not rows:
                    st.info("尚無已結算薪資紀錄。")
                else:
                    out = []
                    for r in rows:
                        d = r._asdict()
                        d["實發／應付淨額 (₫)"] = _fmt_vnd(d.pop("net_pay"))
                        out.append(d)
                    st.dataframe(pd.DataFrame(out), use_container_width=True, hide_index=True)
        except Exception:
            st.info("尚無已結算薪資紀錄。")


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
