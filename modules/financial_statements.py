import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def format_vnd(amount):
    try:
        val = float(amount)
        return f"{val:,.0f}".replace(",", ".") + " VND"
    except Exception:
        return f"{amount} VND"

def calculate_custom_depreciation(cost, salvage, purchase_date_str, useful_years):
    try:
        cost_val = float(cost or 0)
        years = int(useful_years or 5)
        if years < 1:
            years = 1
        total_months = years * 12
        salvage_val = float(salvage if salvage is not None else (cost_val * 0.1))
        
        if isinstance(purchase_date_str, (datetime.date, datetime.datetime)):
            p_date = purchase_date_str
        else:
            p_date = datetime.datetime.strptime(str(purchase_date_str)[:10], "%Y-%m-%d").date()
            
        today = datetime.date.today()
        months_used = (today.year - p_date.year) * 12 + (today.month - p_date.month)
        if months_used < 0:
            months_used = 0
            
        total_depreciable_base = max(0.0, cost_val - salvage_val)
        monthly_depreciation = total_depreciable_base / float(total_months)
        
        accumulated_depr = min(total_depreciable_base, monthly_depreciation * months_used)
        current_net_value = max(salvage_val, cost_val - accumulated_depr)
        
        return months_used, accumulated_depr, current_net_value
    except Exception:
        return 0, 0.0, float(cost or 0)

def render_financial_statements_page(engine=None, lang="繁體中文", **kwargs):
    st.title("📑 越南稅務標準財務總表 (BCTC / Thông tư 200)")
    st.caption("依據越南企業會計制度自動彙整固定資產淨值、營運資產與財務狀況總表。")

    total_asset_cost = 0.0
    total_net_book_value = 0.0
    total_accumulated_depr = 0.0
    bctc_rows = []

    if engine:
        try:
            with engine.connect() as conn:
                res = conn.execute(text("SELECT * FROM public.fixed_assets;"))
                rows = res.fetchall()
                for r in rows:
                    item = dict(r._mapping)
                    cost = float(item.get("cost_amount", 0) or 0)
                    salvage = float(item.get("salvage_amount", 0) or (cost * 0.1))
                    p_date = item.get("purchase_date") or datetime.date(2023, 1, 1)
                    life_years = int(item.get("useful_life_years") or 5)
                    
                    _, accum, net = calculate_custom_depreciation(cost, salvage, p_date, life_years)
                    
                    total_asset_cost += cost
                    total_accumulated_depr += accum
                    total_net_book_value += net
                    
                    bctc_rows.append({
                        "代碼": item.get("asset_code"),
                        "資產名稱": item.get("asset_name"),
                        "分類": item.get("category"),
                        "耐用年限": f"{life_years}年",
                        "取得原價 (Cost)": format_vnd(cost),
                        "累積折舊 (Depreciation)": format_vnd(accum),
                        "帳面淨值 (Net Book Value)": format_vnd(net)
                    })
        except Exception:
            pass

    col_1, col_2, col_3 = st.columns(3)
    col_1.metric("🏢 固定資產總成本 (Total Cost)", format_vnd(total_asset_cost))
    col_2.metric("📉 累積折舊總額 (Accumulated Depr.)", format_vnd(total_accumulated_depr))
    col_3.metric("💰 帳面淨值總計 (Net Book Value)", format_vnd(total_net_book_value))

    st.markdown("---")
    st.markdown("#### 📊 固定資產會計總表明細 (B01-DN 格式彙整)")
    if bctc_rows:
        st.dataframe(pd.DataFrame(bctc_rows), use_container_width=True)
    else:
        st.info("目前尚無資產數據可供彙總。")

    st.markdown("---")
    st.markdown("#### 📈 越南 Thông tư 200 會計科目結構總結")
    st.markdown(f"""
    * **100. 短期資產 (Short-term Assets)**：包含銀行存款、應收帳款與存貨。
    * **200. 長期資產 (Long-term Assets)**：
      * **221. 有形固定資產 (Tangible Fixed Assets)**：成本 `{format_vnd(total_asset_cost)}` 減除累積折舊 `{format_vnd(total_accumulated_depr)}`，淨值 `{format_vnd(total_net_book_value)}`。
    * **300. 負債總計 (Liabilities)**：包含應付帳款、短期貸款。
    * **400. 股東權益 (Equity)**：投資主資本與累計未分配盈餘。
    """)

# 相容性進入點
def show(engine=None, lang="繁體中文", **kwargs):
    render_financial_statements_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_financial_statements_page(engine=engine, lang=lang, **kwargs)
