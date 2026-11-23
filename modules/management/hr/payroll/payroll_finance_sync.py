# ==========================================
# 檔案路徑：modules/management/hr/payroll/payroll_finance_sync.py
# 職責：L2 行政／人事 - 薪資與公司雇主負擔社保連動財務報表（獨立模組）
# ==========================================

import pandas as pd
import streamlit as st
from sqlalchemy import text


def _fmt_vnd(val: float | int) -> str:
    try:
        return f"{round(float(val or 0)):,}".replace(",", ".") + " ₫"
    except Exception:
        return "0 ₫"


def ensure_finance_payroll_sync_table(engine):
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    CREATE TABLE IF NOT EXISTS public.fin_payroll_social_ins_entries (
                        id SERIAL PRIMARY KEY,
                        tenant_id VARCHAR(64) NOT NULL,
                        pay_month VARCHAR(16) NOT NULL,
                        entry_type VARCHAR(64) NOT NULL,
                        account_code VARCHAR(32) DEFAULT '6422',
                        account_name VARCHAR(120) DEFAULT '公司負擔社會保險費',
                        amount_vnd NUMERIC(18, 2) DEFAULT 0,
                        headcount INT DEFAULT 0,
                        emp_deduction_vnd NUMERIC(18, 2) DEFAULT 0,
                        company_si_vnd NUMERIC(18, 2) DEFAULT 0,
                        net_payroll_vnd NUMERIC(18, 2) DEFAULT 0,
                        synced_by VARCHAR(100),
                        synced_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (tenant_id, pay_month, entry_type)
                    );
                """)
            )
    except Exception:
        pass


def sync_payroll_and_company_si_to_finance(
    engine,
    tenant_id: str,
    pay_month: str,
    headcount: int,
    emp_ded_total: float,
    company_si_total: float,
    net_pay_total: float,
    synced_by: str,
):
    ensure_finance_payroll_sync_table(engine)
    records = [
        {
            "entry_type": "COMPANY_SOCIAL_INSURANCE",
            "account_code": "6422",
            "account_name": "公司負擔社會保險 (BHXH/BHYT/BHTN - 雇主)",
            "amount_vnd": round(float(company_si_total), 0),
        },
        {
            "entry_type": "EMP_SOCIAL_INSURANCE_DEDUCTION",
            "account_code": "3383",
            "account_name": "代扣員工社會保險 (BHXH/BHYT/BHTN - 員工)",
            "amount_vnd": round(float(emp_ded_total), 0),
        },
        {
            "entry_type": "NET_PAYROLL_PAYABLE",
            "account_code": "334",
            "account_name": "應付員工薪資總計（實發）",
            "amount_vnd": round(float(net_pay_total), 0),
        },
    ]

    with engine.begin() as conn:
        for rec in records:
            conn.execute(
                text("""
                    INSERT INTO public.fin_payroll_social_ins_entries (
                        tenant_id, pay_month, entry_type, account_code, account_name,
                        amount_vnd, headcount, emp_deduction_vnd, company_si_vnd,
                        net_payroll_vnd, synced_by, synced_at
                    )
                    VALUES (
                        :tid, :pm, :etype, :acode, :aname,
                        :amt, :hc, :empc, :cosi,
                        :netp, :sby, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (tenant_id, pay_month, entry_type) DO UPDATE SET
                        account_code = EXCLUDED.account_code,
                        account_name = EXCLUDED.account_name,
                        amount_vnd = EXCLUDED.amount_vnd,
                        headcount = EXCLUDED.headcount,
                        emp_deduction_vnd = EXCLUDED.emp_deduction_vnd,
                        company_si_vnd = EXCLUDED.company_si_vnd,
                        net_payroll_vnd = EXCLUDED.net_payroll_vnd,
                        synced_by = EXCLUDED.synced_by,
                        synced_at = CURRENT_TIMESTAMP
                """),
                {
                    "tid": tenant_id,
                    "pm": pay_month,
                    "etype": rec["entry_type"],
                    "acode": rec["account_code"],
                    "aname": rec["account_name"],
                    "amt": rec["amount_vnd"],
                    "hc": int(headcount),
                    "empc": round(float(emp_ded_total), 0),
                    "cosi": round(float(company_si_total), 0),
                    "netp": round(float(net_pay_total), 0),
                    "sby": synced_by,
                },
            )


def render_finance_sync_panel(
    engine,
    tenant_id: str,
    pay_month: str,
    headcount: int,
    emp_ded_total: float,
    company_si_total: float,
    net_pay_total: float,
    current_user: str = "admin",
):
    st.divider()
    st.markdown("#### 📊 連動財務報表：公司雇主負擔社保與薪資彙總")
    st.caption("將當月「公司雇主負擔社保」、「代扣員工社保」與「實發薪資」同步至財務報表分錄表（依月份覆蓋更新，避免重複加總）。")

    if st.button("📤 同步／拋轉當月公司社保與薪資至財務報表", type="primary", use_container_width=True, key="btn_sync_fin_si"):
        if not engine:
            st.error("❌ 尚未連線資料庫，無法同步至財務報表。")
        else:
            try:
                sync_payroll_and_company_si_to_finance(
                    engine=engine,
                    tenant_id=tenant_id,
                    pay_month=pay_month,
                    headcount=headcount,
                    emp_ded_total=emp_ded_total,
                    company_si_total=company_si_total,
                    net_pay_total=net_pay_total,
                    synced_by=current_user,
                )
                st.success(f"✅ 已將【{pay_month}】公司雇主負擔社保（{_fmt_vnd(company_si_total)}）與薪資結算同步至財務報表。")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 同步失敗：{e}")

    if engine:
        try:
            with engine.connect() as conn:
                f_rows = conn.execute(
                    text("""
                        SELECT pay_month, account_code, account_name, amount_vnd, headcount, synced_by, synced_at::text
                        FROM public.fin_payroll_social_ins_entries
                        WHERE tenant_id = :tid AND pay_month = :pm
                        ORDER BY id ASC
                    """),
                    {"tid": tenant_id, "pm": pay_month},
                ).fetchall()
                if f_rows:
                    f_df = pd.DataFrame([r._asdict() for r in f_rows])
                    f_df["金額"] = f_df["amount_vnd"].apply(_fmt_vnd)
                    st.dataframe(
                        f_df.rename(columns={
                            "pay_month": "月份",
                            "account_code": "會計科目",
                            "account_name": "財報／會計項目",
                            "headcount": "計薪人數",
                            "synced_by": "同步人",
                            "synced_at": "同步時間",
                        })[["月份", "會計科目", "財報／會計項目", "金額", "計薪人數", "同步人", "同步時間"]],
                        use_container_width=True,
                        hide_index=True,
                    )
        except Exception:
            pass
