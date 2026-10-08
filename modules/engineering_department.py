import streamlit as st
import pandas as pd
import datetime

def render_engineering_department_page(engine=None, lang="繁體中文", **kwargs):
    st.title("🛠️ 裕豐電機工業 - 工程管理中心與設計部門")
    st.caption("涵蓋工程報價系統、水電工程驗收與進度追蹤（連動財務應收帳款 AR）、現場日報表與設計圖庫 Storage。")

    # 🎯 精準攔截左側選單傳入的動作或預設功能
    sub_action = (
        kwargs.get("sub_action") 
        or st.session_state.get("current_sub_action") 
        or st.session_state.get("selected_sub_menu")
        or st.session_state.get("sub_menu")
        or "1"
    )
    
    sub_str = str(sub_action)
    if "驗收" in sub_str or "進度" in sub_str or "2" in sub_str:
        current_mode = "progress"
    elif "日報" in sub_str or "出工" in sub_str or "3" in sub_str:
        current_mode = "daily"
    elif "設計" in sub_str or "Storage" in sub_str or "圖庫" in sub_str or "4" in sub_str:
        current_mode = "design"
    else:
        current_mode = "quote"

    # ====================================================
    # 1. ⚙️ 配電盤與工程專案報價系統
    # ====================================================
    if current_mode == "quote":
        st.markdown("### ⚙️ 1. 配電盤與工程專案報價系統 (Quotation & AR Transfer)")
        st.markdown("#### 📋 工程專案基本資訊")
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            vendor_name = st.text_input("廠商名稱", value="Công ty TNHH Xây lắp Tân Thuận")
        with c2:
            proj_name = st.text_input("工程名稱 / 專案名稱", value="Nhà máy dệt Tây Ninh - Tủ điện chính 2000A")
        with c3:
            currency = st.selectbox("計價幣別", ["USD", "VND", "TWD"])

        st.markdown("#### 📦 報價內容明細 (連動倉庫庫存與單價)")
        warehouse_items = [
            {"code": "CU-BUS-10100", "name": "銅排 Busbar 10x100mm", "stock": 450.0, "price": 12.50},
            {"code": "CB-ACB-2000A", "name": "空氣斷路器 ACB 2000A", "stock": 8.0, "price": 1850.00},
            {"code": "CB-MCCB-250A", "name": "塑殼斷路器 MCCB 250A", "stock": 35.0, "price": 145.00}
        ]

        subtotal = 0.0
        for idx, wh in enumerate(warehouse_items):
            cols = st.columns([1.5, 3, 1, 1, 1, 1.5])
            with cols[0]:
                st.text_input(f"C_{idx}", value=wh["code"], disabled=True, label_visibility="collapsed")
            with cols[1]:
                st.text_input(f"N_{idx}", value=wh["name"], disabled=True, label_visibility="collapsed")
            with cols[2]:
                st.metric(label="庫存", value=f"{wh['stock']}", label_visibility="collapsed")
            with cols[3]:
                qty = st.number_input(f"Q_{idx}", min_value=0.0, value=10.0 if idx==0 else 1.0, step=1.0, label_visibility="collapsed")
            with cols[4]:
                st.text_input(f"P_{idx}", value=f"${wh['price']}", disabled=True, label_visibility="collapsed")
            with cols[5]:
                line_t = qty * wh["price"]
                subtotal += line_t
                st.text_input(f"T_{idx}", value=f"${line_t:,.2f}", disabled=True, label_visibility="collapsed")

        st.markdown("---")
        st.metric(label="未稅金額總計 (Subtotal)", value=f"${subtotal:,.2f}")
        
        if st.button("🚀 一鍵傳動至財務應收帳款 (AR) 系統", type="primary", use_container_width=True):
            st.success(f"✅ 成功將專案 [{proj_name}] 報價金額傳動至財務部應收帳款（AR）模組！")

    # ====================================================
    # 2. ⚡ 水電工程驗收與進度追蹤 (連動 AR)
    # ====================================================
    elif current_mode == "progress":
        st.markdown("### ⚡ 2. 水電工程驗收、進度追蹤與 AR 應收款連動中心")
        st.caption("即時監控工程施工進度、預定驗收時間，並與財務部應收帳款（AR）即時通訊連動進行請款催收。")

        kc1, kc2, kc3, kc4 = st.columns(4)
        with kc1:
            st.metric("在手水電專案", "4 件", "執行中 3 / 待驗收 1")
        with kc2:
            st.metric("合約總金額", "$1,850,000", "USD")
        with kc3:
            st.metric("總未收款 (AR)", "$600,000", "🔴 需加強催收")
        with kc4:
            st.metric("平均工程進度", "76.5%", "● 正常")

        st.markdown("---")
        st.markdown("#### 📋 專案進度、驗收時間表與 AR 應收款即時連動管控表")
        
        data = [
            {"代碼": "PRJ-01", "客戶": "越南新順楠梓電子廠", "項目": "無塵室高低壓配電安裝", "合約總值": "$450,000", "已收": "$315,000", "未收AR": "$135,000", "進度": "90%", "驗收日": "2026-10-15 (初驗)", "狀態": "🟢 待驗收"},
            {"代碼": "PRJ-02", "客戶": "平陽美德金屬加工廠", "項目": "廠房動力配電與照明工程", "合約總值": "$380,000", "已收": "$228,000", "未收AR": "$152,000", "進度": "75%", "驗收日": "2026-10-28 (複驗)", "狀態": "🟡 施工中"},
            {"代碼": "PRJ-03", "客戶": "隆安宏遠精密機械廠", "項目": "變電站統包與銅排配置", "合約總值": "$620,000", "已收": "$434,000", "未收AR": "$186,000", "進度": "85%", "驗收日": "2026-11-05 (正式驗收)", "狀態": "🟢 主體完工"}
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True)

        st.markdown("---")
        st.info("🔗 **財務 AR 即時連動**：當工程進度達標或完成驗收時，可點擊下方按鈕將資料即時拋轉至財務應收帳款模組進行催收。")
        if st.button("📡 立即同步驗收進度並通知財務 AR 進行請款催收", type="primary"):
            st.success("✅ 已成功向財務部應收帳款（AR）發送即時通知與驗收時間表！")

    # ====================================================
    # 3. 📝 現場工程日報表與出工統計
    # ====================================================
    elif current_mode == "daily":
        st.markdown("### 📝 3. 現場工程日報表與出工統計 (Daily Site Reports)")
        st.caption("記錄每日台幹與越籍工人出工數、施工進度摘要與工地異常狀況回報。")
        
        if "daily_reports" not in st.session_state:
            st.session_state.daily_reports = [
                {"日期": "2026-10-07", "案場": "越南西寧廠", "負責台幹": "admin", "工人數": 18, "施工摘要": "完成主母線銅排架設與耐壓測試。"}
            ]
        
        st.markdown("#### 📋 近期現場施工日報紀錄")
        st.dataframe(pd.DataFrame(st.session_state.daily_reports), use_container_width=True)

        st.markdown("---")
        st.markdown("#### ➕ 填寫今日施工日報表")
        with st.form("daily_form"):
            dc1, dc2 = st.columns(2)
            with dc1:
                d_plant = st.selectbox("案場廠區", ["越南西寧廠", "越南海防廠", "外部工程工地"])
                d_workers = st.number_input("越籍工人數", min_value=1, value=15)
            with dc2:
                d_leader = st.text_input("負責台幹", value="admin")
                d_date = st.date_input("施工日期", value=datetime.date.today())
            
            d_summary = st.text_area("當日施工摘要與異常回報", placeholder="例如: 進行配電盤銅排組裝與穿線作業，無異常。")
            
            if st.form_submit_button("💾 提交現場施工日報表", type="primary"):
                st.session_state.daily_reports.insert(0, {
                    "日期": str(d_date), 
                    "案場": d_plant, 
                    "負責台幹": d_leader, 
                    "工人數": d_workers, 
                    "施工摘要": d_summary
                })
                st.success("✅ 現場施工日報表已成功提交並歸檔！")
                st.rerun()

    # ====================================================
    # 4. 📐 配電盤電氣與機構設計圖庫 Storage
    # ====================================================
    elif current_mode == "design":
        st.markdown("### 📐 4. 配電盤電氣與機構設計圖庫 Storage 雲端中心")
        st.caption("設計工程師可在此上傳 CAD/PDF/圖片圖檔至公司內部 Storage，供管理中心與各廠區直接下載。")
        
        if "storage_drawings" not in st.session_state:
            st.session_state.storage_drawings = [
                {"圖號": "DWG-01", "專案名稱": "越南新順電子廠", "檔案名稱": "MSB_2000A.pdf", "上傳時間": "2026-10-01", "上傳人": "An"}
            ]
        
        criteria_col1, criteria_col2 = st.columns([3, 1])
        with criteria_col1:
            st.markdown("#### 📂 公司內部 Storage 現有圖庫列表")
        with criteria_col2:
            st.info("共 1 套圖檔")

        st.dataframe(pd.DataFrame(st.session_state.storage_drawings), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 📤 上傳新設計圖檔至公司 Storage")
        with st.form("upload_form"):
            uc1, uc2 = st.columns(2)
            with uc1:
                dwg_no = st.text_input("圖號編碼 (Drawing No.)", placeholder="例如: DWG-2026-05")
            with uc2:
                dwg_name = st.text_input("專案/圖檔名稱", placeholder="例如: 海防廠控制盤配置圖")
            
            up_file = st.file_uploader("選擇設計圖檔 (PDF, DWG, PNG, JPG)", type=["pdf", "dwg", "png", "jpg"])
            
            if st.form_submit_button("💾 儲存並上傳至 Storage", type="primary"):
                if dwg_no and dwg_name and up_file:
                    st.session_state.storage_drawings.insert(0, {
                        "圖號": dwg_no, 
                        "專案名稱": dwg_name, 
                        "檔案名稱": up_file.name, 
                        "上傳時間": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), 
                        "上傳人": "admin"
                    })
                    st.success("✅ 設計圖檔已成功上傳至 Storage 雲端中心！")
                    st.rerun()
                else:
                    st.warning("⚠️ 請完整填寫圖號、專案名稱並上傳檔案！")

# ----------------------------------------------------
# 🔗 相容性進入點定義
# ----------------------------------------------------
def show(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def render_engineering_department(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)
