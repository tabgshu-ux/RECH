import streamlit as st
import pandas as pd

def render_financials_pl_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📊 財務與損益摘要 (AR / AP 與會計報表)")
    st.caption("提供應收應付帳款餘額與越南財政部 Thông tư 200 標準會計報表總覽。")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 應收帳款明細 (AR)")
        ar_data = [
            {"客戶名稱": "越南新順電子廠", "應收金額": "35,000,000,000 ₫", "狀態": "正常執行"},
            {"客戶名稱": "平陽美德金屬加工廠", "應收金額": "48,630,132,003 ₫", "狀態": "屆期催收"},
            {"客戶名稱": "隆安宏遠精密機械", "應收金額": "58,000,000,000 ₫", "狀態": "額度內正常"}
        ]
        st.dataframe(pd.DataFrame(ar_data), use_container_width=True)

    with col2:
        st.markdown("#### 🛒 應付帳款明細 (AP)")
        ap_data = [
            {"供應商": "越南銅業股份有限公司", "應付金額": "18,200,000,000 ₫", "狀態": "票期正常"},
            {"供應商": "施耐德電機零組件 (Schneider)", "應付金額": "12,500,000,000 ₫", "狀態": "列入本期應付"},
            {"供應商": "在地外包工班", "應付金額": "4,500,000,000 ₫", "狀態": "待審查"}
        ]
        st.dataframe(pd.DataFrame(ap_data), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📈 越南會計準則 Thông tư 200 財務報表")
    
    t200_tab1, t200_tab2 = st.tabs([
        "資產負債表 (Bảng Cân đối kế toán)", 
        "綜合損益表 (Báo cáo kết quả hoạt động kinh doanh)"
    ])
    
    with t200_tab1:
        bs_data = [
            {"代碼": "100", "資產項目 (Tài sản)": "A. 流動資產 (Tài sản ngắn hạn)", "金額 (VND)": "215,400,000,000"},
            {"代碼": "110", "資產項目 (Tài sản)": "  1. 現金及約當現金", "金額 (VND)": "45,200,000,000"},
            {"代碼": "130", "資產項目 (Tài sản)": "  2. 應收帳款淨額", "金額 (VND)": "141,630,132,003"},
            {"代碼": "150", "資產項目 (Tài sản)": "  3. 存貨", "金額 (VND)": "28,569,867,997"},
            {"代碼": "200", "資產項目 (Tài sản)": "B. 非流動資產 (Tài sản dài hạn)", "金額 (VND)": "95,000,000,000"},
            {"代碼": "220", "資產項目 (Tài sản)": "  1. 固定資產", "金額 (VND)": "95,000,000,000"},
            {"代碼": "270", "資產項目 (Tài sản)": "資產總計 (TỔNG CỘNG TÀI SẢN)", "金額 (VND)": "310,400,000,000"}
        ]
        st.dataframe(pd.DataFrame(bs_data), use_container_width=True)

    with t200_tab2:
        pl_data = [
            {"代碼": "01", "項目 (Chỉ tiêu)": "營業收入總額", "金額 (VND)": "185,000,000,000"},
            {"代碼": "10", "項目 (Chỉ tiêu)": "營業成本", "金額 (VND)": "142,000,000,000"},
            {"代碼": "20", "項目 (Chỉ tiêu)": "營業毛利", "金額 (VND)": "43,000,000,000"},
            {"代碼": "30", "項目 (Chỉ tiêu)": "營業費用", "金額 (VND)": "15,400,000,000"},
            {"代碼": "50", "項目 (Chỉ tiêu)": "稅前淨利", "金額 (VND)": "27,600,000,000"},
            {"代碼": "60", "項目 (Chỉ tiêu)": "稅後淨利", "金額 (VND)": "22,080,000,000"}
        ]
        st.dataframe(pd.DataFrame(pl_data), use_container_width=True)

def show(engine=None, lang="繁體中文", **kwargs):
    render_financials_pl_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_financials_pl_page(engine=engine, lang=lang, **kwargs)
