# ==========================================
# 檔案路徑：modules/management/legal_finance/budget_tax_bi.py
# 職責：L2 財務／會計（管理部底下）- 預算控管、越南稅務／發票與多維度財報摘要
# ==========================================

import pandas as pd
import streamlit as st
from sqlalchemy import text
from core import ui_theme


def _fmt_vnd(val: float | int) -> str:
    return f"{round(float(val or 0)):,}".replace(",", ".")


def render(engine=None, lang="zh", **kwargs):
    _ = ui_theme.norm_lang(lang or st.session_state.get("current_lang", "zh"))
    tenant_id = st.session_state.get("tenant_id", "REETECH_VN")

    st.markdown("### 📈 預算控管、越南稅務／發票與多維度財報（L2 財務／管理部）")
    st.caption("檢視應收／應付、總務與點工支出與越南 VAT／發票申報檢核摘要，並預留 Thông tư 200 法定報表與 invoice_id 串聯。")

    ar_v, ap_v, worker_v, ga_v = 380000000.0, 190000000.0, 0.0, 102100000.0
    if engine:
        try:
            with engine.connect() as conn:
                r_ar = conn.execute(
                    text("SELECT COALESCE(SUM(amount_vnd), 0) FROM fin_ledger_entries WHERE tenant_id = :tid AND category ILIKE '%AR%'"),
                    {"tid": tenant_id},
                ).scalar()
                r_ap = conn.execute(
                    text("SELECT COALESCE(SUM(amount_vnd), 0) FROM fin_ledger_entries WHERE tenant_id = :tid AND category ILIKE '%AP%'"),
                    {"tid": tenant_id},
                ).scalar()
                if r_ar:
                    ar_v = float(r_ar)
                if r_ap:
                    ap_v = float(r_ap)
        except Exception:
            pass
        try:
            with engine.connect() as conn:
                r_wk = conn.execute(
                    text("SELECT COALESCE(SUM(total_amount_vnd), 0) FROM hr_daily_worker_logs WHERE tenant_id = :tid"),
                    {"tid": tenant_id},
                ).scalar()
                worker_v = float(r_wk or 0)
        except Exception:
            pass
        try:
            with engine.connect() as conn:
                r_ga = conn.execute(
                    text("SELECT COALESCE(SUM(amount_vnd), 0) FROM ga_expense_items WHERE tenant_id = :tid"),
                    {"tid": tenant_id},
                ).scalar()
                if r_ga:
                    ga_v = float(r_ga)
        except Exception:
            pass

    c1, c2, c3 = st.columns(3)
    c1.metric("應收帳款 (AR)", f"{_fmt_vnd(ar_v)} ₫")
    c2.metric("應付帳款 (AP)", f"{_fmt_vnd(ap_v)} ₫")
    c3.metric("點工＋總務支出彙總", f"{_fmt_vnd(worker_v + ga_v)} ₫")

    st.divider()
    st.markdown("#### 🧾 越南稅務與發票申報檢核項目")
    tax_rows = [
        {"檢核項目": "Hóa đơn điện tử (越南電子發票)", "申報週期": "按次／月度", "狀態": "待核對進銷項發票", "備註": "請核對供應商稅碼 (MST) 與發票號碼"},
        {"檢核項目": "Thuế GTGT (增值稅 VAT)", "申報週期": "月／季申報", "狀態": "進行中", "備註": "區分可扣抵進項與案場請款銷項"},
        {"檢核項目": "Báo cáo tài chính (Thông tư 200)", "申報週期": "月／季／年度", "狀態": "結構已預留", "備註": "可串接完整會計科目與損益／資產負債表"},
    ]
    st.dataframe(pd.DataFrame(tax_rows), use_container_width=True, hide_index=True)


def show(engine=None, lang="zh", **kwargs):
    render(engine=engine, lang=lang, **kwargs)
