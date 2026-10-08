import streamlit as st
import pandas as pd
import datetime

def render_engineering_department_page(engine=None, lang="繁體中文", **kwargs):
    st.title("🛠️ 裕豐電機工業 - 工程管理中心與設計部門")
    st.caption("涵蓋工程報價系統、工程驗收與進度追蹤（連動財務應收帳款 AR）、現場日報表與設計圖庫 Storage。")

    # 🎯 嚴格解析選單動作，確保子功能完全獨立切換
    sub_action = (
        kwargs.get("sub_action") 
        or st.session_state.get("current_sub_action") 
        or st.session_state.get("selected_sub_menu")
        or st.session_state.get("sub_menu")
        or "1"
    )
    
    sub_str = str(sub_action).strip()
    
    if "驗收" in sub_str or "進度" in sub_str or sub_str in ["2", "工程驗收與進度追蹤"]:
        current_mode = "progress"
    elif "日報" in sub_str or "出工" in sub_str or sub_str in ["3", "現場工程日報表與出工統計"]:
        current_mode = "daily"
    elif "設計" in sub_str or "Storage" in sub_str or "圖庫" in sub_str or sub_str in ["4", "配電盤電氣與機構設計圖庫 Storage"]:
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
            vendor_name = st.text_input("廠商名稱", value="Công ty TNHH Xây lắp Tân Thuận", key="q_vendor")
        with c2:
            proj_name = st.text_input("工程名稱 / 專案名稱", value="Nhà máy dệt Tây Ninh - Tủ điện chính 2000A", key="q_proj")
        with c3:
            currency = st.selectbox("計價幣別", ["USD", "VND", "TWD"], key="q_curr")

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
    # 2. ⚡ 工程驗收與進度追蹤 (連動 AR)
    # ====================================================
    elif current_mode == "progress":
        st.markdown("### ⚡ 2. 工程驗收與進度追蹤與 AR 應收款連動中心")
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
        st.markdown("#### 🔍 專案資料搜尋與過濾")
        if "prog_search" not in st.session_state:
            st.session_state.prog_search = ""
        search_query = st.text_input("輸入專案代碼、客戶或項目關鍵字搜尋", value=st.session_state.prog_search, key="prog_search_input")

        if "projects_data" not in st.session_state:
            st.session_state.projects_data = [
                {"代碼": "PRJ-01", "客戶": "越南新順楠梓電子廠", "項目": "無塵室高低壓配電安裝", "合約總值": "$450,000", "已收": "$315,000", "未收AR": "$135,000", "進度": "90%", "驗收日": "2026-10-15 (初驗)", "狀態": "🟢 待驗收"},
                {"代碼": "PRJ-02", "客戶": "平陽美德金屬加工廠", "項目": "廠房動力配電與照明工程", "合約總值": "$380,000", "已收": "$228,000", "未收AR": "$152,000", "進度": "75%", "驗收日": "2026-10-28 (複驗)", "狀態": "🟡 施工中"},
                {"代碼": "PRJ-03", "客戶": "隆安宏遠精密機械廠", "項目": "變電站統包與銅排配置", "合約總值": "$620,000", "已收": "$434,000", "未收AR": "$186,000", "進度": "85%", "驗收日": "2026-11-05 (正式驗收)", "狀態": "🟢 主體完工"}
            ]

        filtered_proj = [
            p for p in st.session_state.projects_data 
            if search_query.lower() in p["代碼"].lower() or search_query.lower() in p["客戶"].lower() or search_query.lower() in p["項目"].lower()
        ] if search_query else st.session_state.projects_data

        st.dataframe(pd.DataFrame(filtered_proj), use_container_width=True)

        st.markdown("#### 🛠️ 專案資料管理 (新增 / 修改 / 刪除)")
        with st.expander("➕ 新增或維護工程專案進度"):
            with st.form("proj_manage_form"):
                pc1, pc2, pc3 = st.columns(3)
                with pc1:
                    new_code = st.text_input("專案代碼", placeholder="例如: PRJ-04")
                    new_cust = st.text_input("客戶名稱", placeholder="例如: 越南海防科技廠")
                with pc2:
                    new_item = st.text_input("工程項目", placeholder="例如: 消防動力系統配電")
                    new_val = st.text_input("合約總值", value="$500,000")
                with pc3:
                    new_ar = st.text_input("未收AR", value="$100,000")
                    new_date = st.text_input("驗收日", value="2026-12-01 (初驗)")
                
                submitted = st.form_submit_button("💾 新增專案進度", type="primary")
                if submitted and new_code:
                    st.session_state.projects_data.append({
                        "代碼": new_code, "客戶": new_cust, "項目": new_item, 
                        "合約總值": new_val, "已收": "$0", "未收AR": new_ar, 
                        "進度": "0%", "驗收日": new_date, "狀態": "🟡 籌備中"
                    })
                    st.success(f"✅ 專案 [{new_code}] 新增成功！")
                    st.rerun()

        del_code = st.selectbox("選擇要刪除的專案代碼", [""] + [p["代碼"] for p in st.session_state.projects_data])
        if st.button("🗑️ 刪除選定專案", type="secondary"):
            if del_code:
                st.session_state.projects_data = [p for p in st.session_state.projects_data if p["代碼"] != del_code]
                st.success(f"✅ 專案 [{del_code}] 已刪除！")
                st.rerun()

        st.markdown("---")
        st.info("🔗 **財務 AR 即時連動**：當工程進度達標或完成驗收時，可點擊下方按鈕將資料即時拋轉至財務應收帳款模組進行催收。")
        if st.button("📡 立即同步驗收進度並通知財務 AR 進行請款催收", type="primary"):
            st.success("✅ 已成功向財務部應收帳款（AR）發送即時通知與驗收時間表！")

    # ====================================================
    # 3. 📝 現場工程日報表與出工統計
    # ====================================================
    elif current_mode == "daily":
        st.markdown("### 📝 3. 現場工程日報表與出工統計 (Daily Site Reports)")
        st.caption("記錄每日台幹與越籍工人數、施工進度摘要與工地異常狀況回報，支援完整搜尋與維護。")
        
        if "daily_reports" not in st.session_state:
            st.session_state.daily_reports = [
                {"日期": "2026-10-07", "案場": "越南西寧廠", "負責台幹": "admin", "工人數": 18, "施工摘要": "完成主母線銅排架設與耐壓測試。"}
            ]
        
        st.markdown("#### 🔍 日報表關鍵字搜尋")
        d_search = st.text_input("輸入案場、負責台幹或摘要關鍵字", key="daily_search_input")
        filtered_daily = [
            r for r in st.session_state.daily_reports 
            if d_search.lower() in r["案場"].lower() or d_search.lower() in r["負責台幹"].lower() or d_search.lower() in r["施工摘要"].lower()
        ] if d_search else st.session_state.daily_reports

        st.markdown("#### 📋 近期現場施工日報紀錄")
        st.dataframe(pd.DataFrame(filtered_daily), use_container_width=True)

        st.markdown("---")
        st.markdown("#### ➕ 填寫今日施工日報表與管理")
        with st.form("daily_form"):
            dc1, dc2 = st.columns(2)
            with dc1:
                d_plant = st.selectbox("案場廠區", ["越南西寧廠", "越南海防廠", "外部工程工地"])
                d_workers = st.number_input("越籍工人數", min_value=1, value=15)
            with dc2:
                d_leader = st.text_input("負責台幹", value="admin")
                d_date = st.date_input("施工日期", value=datetime.date.today())
            
            d_summary = st.text_area("當日施工摘要與異常回報", placeholder="例如: 進行配電盤銅排組裝與穿線作業，無異常。")
            
            if st.form_submit_button("💾 設為今日施工日報表", type="primary"):
                st.session_state.daily_reports.insert(0, {
                    "日期": str(d_date), 
                    "案場": d_plant, 
                    "負責台幹": d_leader, 
                    "工人數": d_workers, 
                    "施工摘要": d_summary
                })
                st.success("✅ 現場施工日報表已成功提交並歸檔！")
                st.rerun()

        del_daily_idx = st.selectbox("選擇要刪除的日報記錄索引", [-1] + list(range(len(st.session_state.daily_reports))), format_func=lambda x: f"索引 {x}: {st.session_state.daily_reports[x]['日期']} - {st.session_state.daily_reports[x]['案場']}" if x >= 0 else "請選擇...")
        if st.button("🗑️ 刪除選定日報紀錄", type="secondary"):
            if del_daily_idx >= 0:
                removed = st.session_state.daily_reports.pop(del_daily_idx)
                st.success(f"✅ 已成功刪除 {removed['日期']} 的日報紀錄！")
                st.rerun()

    # ====================================================
    # 4. 📐 配電盤電氣與機構設計圖庫 Storage
    # ====================================================
    elif current_mode == "design":
        st.markdown("### 📐 4. 配電盤電氣與機構設計圖庫 Storage 雲端中心")
        st.caption("設計工程師可在此上傳 CAD/PDF/圖片圖檔至公司內部 Storage，支援圖號搜尋與檔案版本管控。")
        
        if "storage_drawings" not in st.session_state:
            st.session_state.storage_drawings = [
                {"圖號": "DWG-01", "專案名稱": "越南新順電子廠", "檔案名稱": "MSB_2000A.pdf", "上傳時間": "2026-10-01", "上傳人": "An"}
            ]
        
        criteria_col1, criteria_col2 = st.columns([3, 1])
        with criteria_col1:
            st.markdown("#### 📂 公司內部 Storage 現有圖庫列表")
        with criteria_col2:
            st.info(f"共 {len(st.session_state.storage_drawings)} 套圖檔")

        dwg_search = st.text_input("輸入圖號或專案名稱搜尋圖檔", key="dwg_search_input")
        filtered_dwg = [
            d for d in st.session_state.storage_drawings 
            if dwg_search.lower() in d["圖號"].lower() or dwg_search.lower() in d["專案名稱"].lower() or dwg_search.lower() in d["檔案名稱"].lower()
        ] if dwg_search else st.session_state.storage_drawings

        st.dataframe(pd.DataFrame(filtered_dwg), use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### 📤 上傳或刪除設計圖檔")
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

        del_dwg_no = st.selectbox("選擇要刪除的圖號", [""] + [d.get("圖號", d.get("图號", "")) for d in st.session_state.storage_drawings], key="del_dwg_select")
        if st.button("🗑️ 刪除選定圖檔", type="secondary"):
            if del_dwg_no:
                st.session_state.storage_drawings = [d for d in st.session_state.storage_drawings if d.get("圖號") != del_dwg_no and d.get("图號") != del_dwg_no]
                st.success(f"✅ 圖號 [{del_dwg_no}] 已從 Storage 移除！")
                st.rerun()

# ----------------------------------------------------
# 🔗 相容性進入點定義
# ----------------------------------------------------
def show(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def main(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)

def render_engineering_department(*args, **kwargs):
    render_engineering_department_page(*args, **kwargs)
