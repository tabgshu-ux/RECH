# 1. 金額即時轉千分號的輔助函數
def format_currency_input(raw_value):
    """將純數字轉為帶點的千分號字串 (越南慣用點作為千分號，例如 13.200.000)"""
    clean_val = re.sub(r"[^\d]", "", str(raw_value))
    if not clean_val:
        return ""
    try:
        val = int(clean_val)
        return f"{val:,.0f}".replace(",", ".")
    except Exception:
        return clean_val

# 2. 在 Streamlit 畫面中的應用範例
salary_input_str = st.text_input(
    "越南盾在地底薪 (Lương CB - VND)", 
    value="13.200.000"
)

# 即時在下方或旁邊幫使用者標註轉換後的清晰金額
parsed_salary = parse_formatted_amount(salary_input_str)
st.caption(f"💡 金額即時預覽：**{parsed_salary:,.0f} VND** （約為清爽好讀格式）")
