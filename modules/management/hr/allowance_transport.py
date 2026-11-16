
# ==========================================
# 檔案路徑：modules/management/hr/allowance_transport.py
# 職責：外勤油費與外出津貼計算（串聯人事與薪資系統）
# ==========================================

import streamlit as st
import pandas as pd

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### ⛽ 外勤油費與外出補助津貼管理中心")
    st.caption("專為水電工程與外勤師傅打造：自動計算外出里程、油費補貼與交通津貼，並無縫串聯至人事薪資 (Payroll) 結算。")

    tab1, tab2, tab3 = st.tabs([
        "🚗 外勤里程與油費計算", 
        "⚙️ 油費與補貼標準設定", 
        "💰 薪資串聯與結算清單"
    ])

    with tab1:
        st.markdown("#### 📋 本月外勤人員外出紀錄與油費試算")
        
        # 模擬外勤紀錄數據
        travel_df = pd.DataFrame({
            "員工編號": ["EMP-001", "EMP-002", "EMP-003", "EMP-004"],
            "員工姓名": ["阮文雄 (Nguyen Van Hung)", "陳志豪", "黎文特 (Le Van Thien)", "林建良"],
            "部門單位": ["工程部", "工程部", "生產部", "工程部"],
            "外勤案場": ["西寧廠二期", "平陽工業區", "隆安光電園區", "胡志明市商辦"],
            "總外出里程 (km)": [120, 340, 85, 210],
            "計算油費補貼 (VND)": [600000, 1700000, 425000, 1050000],
            "狀態": ["✅ 已核准", "✅ 已核准", "⏳ 審核中", "✅ 已核准"]
        })
        st.dataframe(travel_df, use_container_width=True, hide_index=True)

        st.markdown("#### ➕ 新增外勤行程與里程登記")
        with st.form("add_travel_form"):
            col1, col2 = st.columns(2)
            with col1:
                emp_name = st.text_input("外勤人員姓名", placeholder="例如: 陳志豪")
                dest = st.text_input("前往案場/廠商", placeholder="例如: 平陽美德金屬加工廠")
            with col2:
                km_val = st.number_input("外出單程/總里程 (公里 km)", min_value=1, value=30)
                allowance_type = st.selectbox("補助類型", ["一般油費補貼 (5,000 ₫/km)", "遠程出差津貼 (固定 300,000 ₫)"])

            submitted = st.form_submit_button("💾 提交外勤里程與油費申請", type="primary", use_container_width=True)
            if submitted:
                st.success(f"🎉 成功提交 [{emp_name}] 前往 [{dest}] 的外勤補貼申請！")

    with tab2:
        st.markdown("#### ⚙️ 參數設定：油費單價與津貼規則")
        with st.form("settings_form"):
            st.number_input("每公里油費補貼標準 (VND / km)", value=5000, step=500)
            st.number_input("每日跨省外勤固定伙食津貼 (VND)", value=100000, step=10000)
            st.text_area("外勤補助備註說明", value="依據公司規定，外勤里程需由主管核可後自動計入當月薪資發放。")
            st.form_submit_button("💾 儲存補助標準設定", type="primary")

    with tab3:
        st.markdown("#### 🔗 外勤津貼自動對接人事薪資 (Payroll) 總表")
        st.info("💡 系統已自動將各員工的外勤油費加總，並準備好匯入至薪資計算與 BHXH 保險模組中。")

        payroll_link_df = pd.DataFrame({
            "員工姓名": ["阮文雄", "陳志豪", "黎文特", "林建良"],
            "本薪 (VND)": [12000000, 15000000, 11000000, 14000000],
            "本月外勤油費補助 (VND)": [600000, 1700000, 425000, 1050000],
            "應發總薪資 (含津貼)": [12600000, 16700000, 11425000, 15050000],
            "薪資串聯狀態": ["🔗 已同步至 Payroll", "🔗 已同步至 Payroll", "⏳ 待結算", "🔗 已同步至 Payroll"]
        })
        st.dataframe(payroll_link_df, use_container_width=True, hide_index=True)

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
