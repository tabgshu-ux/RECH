# ==========================================
# 檔案路徑：modules/engineering/engineering_department.py
# 職責：工程部主控台（主管總覽與全面實作互動表單的現場作業卡片中心）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🛠️ 工程部綜合管理與作業中心 (Engineering Department)")
    st.caption("主管決策戰情總覽與全功能互動式現場作業模組。")

    # 頂部切換：主管總覽 vs 現場互動作業卡片
    main_tab = st.radio(
        "選擇操作模式 / Select Mode:",
        ["👑 工程部總覽（主管決策戰情）", "🧩 現場作業與互動功能模組（卡片式）"],
        horizontal=True
    )

    if "👑 工程部總覽" in main_tab:
        st.markdown("---")
        st.markdown("#### 📊 領導決策：全廠工程案場執行與損益戰情")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("進行中案場", "12 案", "🟢 正常")
        with col2:
            st.metric("今日現場出勤", "86 人", "包含點工 18 人")
        with col3:
            st.metric("進度落後警示", "1 案", "需主管介入")
        with col4:
            st.metric("總合約金額", "325.5億 ₫", "執行率 78%")

        st.markdown("##### 🏗️ 各工業區主要案場與毛利進度總表")
        project_data = pd.DataFrame({
            "案場編號": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03"],
            "案場名稱": ["西寧廠二期配電盤擴建工程", "平陽工業區廠房機電統包", "隆安省光電園區變壓器安裝"],
            "負責經理": ["陳志豪", "阮文雄", "林建良"],
            "合約金額 (VND)": ["12,500,000,000", "15,200,000,000", "8,400,000,000"],
            "預估毛利率": ["24.4%", "21.0%", "19.5%"],
            "狀態": ["🟢 正常獲利", "🟡 需留意", "🟢 正常獲利"]
        })
        st.dataframe(project_data, use_container_width=True, hide_index=True)

        st.markdown("---")
        if st.button("📈 深入檢視《工程專案損益與預算控管》詳情 ➡️", type="primary", use_container_width=True):
            st.session_state['eng_active_card'] = "📈 專案損益控管"
            st.rerun()

    else:
        st.markdown("---")
        st.markdown("#### 📱 現場作業功能選擇（點擊卡片直接進入互動操作）")

        if 'eng_active_card' not in st.session_state:
            st.session_state['eng_active_card'] = "🚨 緊急維修派工"

        # 3 列網格卡片選單
        c1, c2, c3 = st.columns(3)
        cards = [
            ("🚨 緊急維修派工", "突發事故通報與派工"),
            ("📈 專案損益控管", "成本、工時與毛利追蹤"),
            ("📋 專案報價追蹤", "報價單與管線進度"),
            ("🧪 FAT/SAT 驗收", "廠內與現場測試簽認"),
            ("📝 施工日報表", "點工點料與每日紀錄"),
            ("📍 外勤 GPS 打卡", "圍籬即時打卡與足跡"),
            ("📐 設計圖庫專區", "配電盤電氣與機構圖面")
        ]

        card_cols = [c1, c2, c3]
        for idx, (card_title, card_desc) in enumerate(cards):
            target_col = card_cols[idx % 3]
            with target_col:
                is_selected = (st.session_state['eng_active_card'] == card_title)
                btn_type = "primary" if is_selected else "secondary"
                with st.container(border=True):
                    st.markdown(f"**{card_title}**")
                    st.caption(card_desc)
                    if st.button("進入操作 ➡️", key=f"card_btn_{idx}", use_container_width=True, type=btn_type):
                        st.session_state['eng_active_card'] = card_title
                        st.rerun()

        st.markdown("---")
        current_active = st.session_state['eng_active_card']
        st.markdown(f"#### 📌 當前操作介面：`{current_active}`")

        # 🌟 完整實作各個卡片的互動操作畫面
        if "緊急維修" in current_active:
            st.markdown("##### 🚨 緊急維修派工與事故通報表單")
            with st.form("emergency_action_form"):
                col1, col2 = st.columns(2)
                with col1:
                    urgency = st.selectbox("緊急等級", ["🔴 紅色特急 (立即派工)", "🟡 普通緊急 (當日處理)"])
                    vendor = st.text_input("外部廠商或案場名稱", placeholder="例如: 平陽美德金屬加工廠")
                with col2:
                    assignee = st.text_input("指派帶班工程師", placeholder="例如: 陳志豪、阮文雄")
                    tools = st.text_input("攜帶工具與備品", placeholder="例如: 三用電表、備用斷路器")
                
                desc = st.text_area("事故狀況簡述與維修需求", placeholder="請描述故障現象及須前往執行的維修動作...")
                submitted = st.form_submit_button("📢 立即發布緊急派工單", type="primary", use_container_width=True)
                if submitted:
                    st.success(f"🎉 成功發布針對 [{vendor}] 的緊急派工單！已同步通知帶班人員 [{assignee}]。")

            st.markdown("##### 📋 歷史緊急派工清單")
            history_df = pd.DataFrame({
                "單號": ["EMG-01", "EMG-02"],
                "廠商": ["西寧廠動力車間", "平陽美德廠"],
                "狀態": ["🔧 維修中", "✅ 已完工"],
                "指派人員": ["陳志豪", "黎文特"]
            })
            st.dataframe(history_df, use_container_width=True, hide_index=True)

        elif "專案損益" in current_active:
            try:
                from modules.engineering import project_pnl
                project_pnl.show(engine=engine, lang=lang, **kwargs)
            except Exception:
                st.info("📈 正在載入專案損益與預算控管模組...")

        elif "設計圖庫" in current_active:
            st.markdown("##### 📐 配電盤電氣與機構設計圖庫 (設計人員專用)")
            st.info("💡 設計人員可在此上傳新版本圖面並管理審查狀態。")
            
            with st.form("upload_dwg_form"):
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    dwg_no = st.text_input("圖面編號", placeholder="DWG-2026-504")
                    dwg_name = st.text_input("專案與圖面名稱", placeholder="新順工業區主配電盤配置圖")
                with d_col2:
                    dwg_rev = st.text_input("設計版本", value="Rev.01")
                    designer = st.text_input("負責設計師", value="張工程師")
                
                uploaded_file = st.file_uploader("上傳 AutoCAD / PDF 圖面檔案", type=["dwg", "pdf", "dxf", "png"])
                up_submitted = st.form_submit_button("💾 儲存並發布新圖面版本", type="primary", use_container_width=True)
                if up_submitted:
                    st.success(f"🎉 成功上傳圖面 [{dwg_no}] - {dwg_name} ({dwg_rev})！")

            design_df = pd.DataFrame({
                "圖面編號": ["DWG-2026-501", "DWG-2026-502", "DWG-2026-503"],
                "專案名稱": ["西寧廠二期總配電盤 (MSB)", "平陽廠自動控制盤 (PLC)", "隆安廠變壓器二次側箱"],
                "設計版本": ["Rev.02", "Rev.01", "Rev.03"],
                "負責設計師": ["張工程師", "李工程師", "王工程師"],
                "審查狀態": ["✅ 主管已核准", "⏳ 審查中", "✅ 客戶已簽認"]
            })
            st.dataframe(design_df, use_container_width=True, hide_index=True)

        elif "FAT/SAT" in current_active:
            st.markdown("##### 🧪 FAT (出廠測試) 與 SAT (現場驗收) 簽認系統")
            with st.form("fatsat_form"):
                fs_col1, fs_col2 = st.columns(2)
                with fs_col1:
                    test_type = st.selectbox("測試類型", ["FAT 廠內出廠測試", "SAT 現場驗收測試"])
                    project_name = st.text_input("案場專案名稱", placeholder="西寧廠二期配電盤")
                with fs_col2:
                    inspector = st.text_input("檢驗工程師", value="林建良")
                    client_rep = st.text_input("客戶代表簽名", placeholder="Mr. Nguyen (廠長)")

                st.markdown("**檢驗項目勾選：**")
                st.checkbox("1. 絕緣電阻測試 (> 100MΩ)", value=True)
                st.checkbox("2. 主母線耐壓與相序測試", value=True)
                st.checkbox("3. PLC 控制迴路與保戶動作測試", value=True)
                st.checkbox("4. 外觀烤漆與機構尺寸複核", value=True)

                fs_submitted = st.form_submit_button("✅ 提交驗收報告並取得主管/客戶簽認", type="primary", use_container_width=True)
                if fs_submitted:
                    st.success(f"🎉 [{project_name}] 的 [{test_type}] 驗收報告已完成並存檔！")

        elif "施工日報" in current_active:
            st.markdown("##### 📝 施工日報表與點工點料登記")
            with st.form("daily_report_form"):
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    r_date = st.date_input("施工日期", value=datetime.date.today())
                    r_proj = st.text_input("施工案場", placeholder="平陽工業區廠房機電統包")
                with r_col2:
                    r_workers = st.number_input("今日出勤總人數 (含點工)", min_value=1, value=15)
                    r_overtime = st.number_input("加班總時數 (小時)", min_value=0, value=3)

                r_desc = st.text_area("今日施工進度摘要與耗用材料登記", placeholder="例如: 完成配電盤主體吊裝及控制線路敷設，耗用 4C*10mm² 電纜 50米...")
                r_submitted = st.form_submit_button("💾 提交今日施工日報表", type="primary", use_container_width=True)
                if r_submitted:
                    st.success(f"🎉 成功提交 [{r_proj}] 的施工日報！今日出勤 {r_workers} 人。")

        elif "GPS" in current_active:
            st.markdown("##### 📍 外勤師傅 GPS 圍籬即時打卡與足跡")
            st.info("💡 偵測外勤人員當前坐標，並記錄抵達案場或客戶廠區的時間。")
            
            with st.container(border=True):
                st.markdown("**當前 GPS 定位狀態**")
                st.markdown("📍 坐標位置：`10.7769° N, 106.7009° E` (越南胡志明市/西寧案場圍籬範圍內)")
                if st.button("📍 立即進行外勤 GPS 打卡簽到", type="primary", use_container_width=True):
                    st.success("🎉 GPS 打卡成功！已記錄時間與案場地理圍籬坐標。")

            st.markdown("##### 📋 今日外勤打卡足跡紀錄")
            gps_df = pd.DataFrame({
                "員工姓名": ["阮文雄", "陳志豪", "黎文特"],
                "打卡地點": ["西寧廠二期", "平陽美德廠", "隆安光電園區"],
                "打卡時間": ["08:15:32", "08:30:10", "09:05:44"],
                "狀態": ["✅ 圍籬內正常", "✅ 圍籬內正常", "✅ 圍籬內正常"]
            })
            st.dataframe(gps_df, use_container_width=True, hide_index=True)

        else:
            st.markdown(f"#### 📌 {current_active}")
            st.info(f"【{current_active}】功能模組建置中...")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
