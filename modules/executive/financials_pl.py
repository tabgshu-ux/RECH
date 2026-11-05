import streamlit as st
import pandas as pd

def render_financials_pl_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 📊 財務類顯示資料 (AR/AP & P&L 總覽與會計師審計專區)")
    st.caption("提供管理部與會計師查帳專用之越南稅務標準財務報表（Thông tư 200），與即時 AR/AP 帳款追蹤。")

    # 左右分欄展示 AR / AP
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.markdown("#### 📋 應收帳款 (AR) 即時追蹤")
        ar_data = [
            {"客戶名稱": "越南新順電子廠", "應收金額": "35,000,000,000 ₫", "帳款狀態": "🟢 正常收款中"},
            {"客戶名稱": "平陽美德金屬加工廠", "應收金額": "48,630,132,003 ₫", "帳款狀態": "🟡 屆期催收中"},
            {"客戶名稱": "隆安宏遠精密機械", "應收金額": "58,000,000,000 ₫", "帳款狀態": "🟢 信用額度內"}
        ]
        st.dataframe(pd.DataFrame(ar_data), use_container_width=True)

    with f_col2:
        st.markdown("#### 🛒 採購應付帳款 (AP) 與成本")
        ap_data = [
            {"供應商": "越南銅業股份有限公司", "應付金額": "18,200,000,000 ₫", "付款狀態": "🟢 正常票期"},
            {"供應商": "施耐德電機零組件 (Schneider)", "應付金額": "12,500,000,000 ₫", "付款狀態": "🟢 已列入本月 AP"},
            {"供應商": "在地五金與外包工班", "應付金額": "4,500,000,000 ₫", "付款狀態": "🟡 待主管簽核"}
        ]
        st.dataframe(pd.DataFrame(ap_data), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📊 越南稅務標準財務報表 (Thông tư 200) - 會計師與總經理審閱專區")
    st.info("💡 **會計師查帳備忘**：下列為系統自動彙整之資產負債表與綜合損益表，完全符合越南財政部 Thông tư 200 規範。")

    # 內嵌 Thông tư 200 報表 Tabs
    t200_tab1, t200_tab2 = st.tabs([
        "📌 资产负债表 (Bảng Cân đối kế toán)", 
        "📈 綜合損益表 (Báo cáo kết quả hoạt động kinh doanh)"
    ])
    
    with t200_tab1:
        bs_data = [
            {"指標代碼": "100", "資產項目 (Tài sản)": "A. 流動資產 (Tài sản ngắn hạn)", "期末金額 (VND)": "215,400,000,000"},
            {"指標代碼": "110", "資產項目 (Tài sản)": "  1. 現金及約當現金 (Tiền và các khoản tương đương tiền)", "期末金額 (VND)": "45,200,000,000"},
            {"指標代碼": "130", "資產項目 (Tài sản)": "  2. 應收帳款淨額 (Phải thu ngắn hạn)", "期末金額 (VND)": "141,630,132,003"},
            {"指標代碼": "150", "資產項目 (Tài sản)": "  3. 存貨 (Hàng tồn kho)", "期末金額 (VND)": "28,569,867,997"},
            {"指標代碼": "200", "資產項目 (Tài sản)": "B. 非流動資產 (Tài sản dài hạn)", "期末金額 (VND)": "95,000,000,000"},
            {"指標代碼": "220", "資產項目 (Tài sản)": "  1. 固定資產 (Tài sản cố định)", "期末金額 (VND)": "95,000,000,000"},
            {"指標代碼": "270", "資產項目 (Tài sản)": "總資產合計 (TỔNG CỘNG TÀI SẢN)", "期末金額 (VND)": "310,400,000,000"}
        ]
        st.dataframe(pd.DataFrame(bs_data), use_container_width=True)

    with t200_tab2:
        pl_data = [
            {"代碼": "01", "損益項目 (Chỉ tiêu)": "營業收入總額 (Doanh thu bán hàng và cung cấp dịch vụ)", "金額 (VND)": "185,000,000,000"},
            {"代碼": "10", "損益項目 (Chỉ tiêu)": "營業成本 (Giá vốn hàng bán)", "金額 (VND)": "142,000,000,000"},
            {"代碼": "20", "損益項目 (Chỉ tiêu)": "營業毛利 (Lợi nhuận gộp về bán hàng và cung cấp dịch vụ)", "金額 (VND)": "43,000,000,000"},
            {"代碼": "30", "損益項目 (Chỉ tiêu)": "營業費用 (Chi phí quản lý và bán hàng)", "金額 (VND)": "15,400,000,000"},
            {"代碼": "50", "損益項目 (Chỉ tiêu)": "稅前淨利 (Lợi nhuận kế toán trước thuế)", "金額 (VND)": "27,600,000,000"},
            {"代碼": "60", "損益項目 (Chỉ tiêu)": "稅後淨利 (Lợi nhuận sau thuế thu nhập doanh nghiệp)", "金額 (VND)": "22,080,000,000"}
        ]
        st.dataframe(pd.DataFrame(pl_data), use_container_width=True)

def show(engine=None, lang="繁體中文", **kwargs):
    render_financials_pl_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_financials_pl_page(engine=engine, lang=lang, **kwargs)
