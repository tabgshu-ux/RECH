import streamlit as st
import pandas as pd

st.title("每日幹部食堂買菜支出與防浮報稽核")

# 日期輸入
date = st.date_input("日期", pd.Timestamp.today())

# 用餐人數與預算
people = st.number_input("用餐人數", min_value=1, value=12)
budget_per_person = st.number_input("每人預算 (VND)", min_value=0, value=100000)
total_budget = people * budget_per_person
st.write(f"💰 總預算: {total_budget:,} VND")

# 食材採購明細
st.subheader("食材採購明細")
item_name = st.text_input("食材名稱", "豬肉·腿肉/肩肉")
quantity = st.number_input("數量 (公斤)", min_value=0.0, value=1.0)
price_per_kg = st.number_input("單價 (VND/kg)", min_value=0, value=120000)
total_price = quantity * price_per_kg

# 顯示結果
st.write(f"🧾 食材: {item_name}")
st.write(f"數量: {quantity} 公斤")
st.write(f"單價: {price_per_kg:,} VND/kg")
st.write(f"總金額: {total_price:,} VND")

# 儲存資料
if st.button("儲存資料"):
    data = {
        "日期": [date],
        "食材": [item_name],
        "數量(kg)": [quantity],
        "單價(VND/kg)": [price_per_kg],
        "總金額(VND)": [total_price],
        "用餐人數": [people],
        "總預算(VND)": [total_budget]
    }
    df = pd.DataFrame(data)
    st.success("✅ 資料已儲存！")
    st.dataframe(df)
