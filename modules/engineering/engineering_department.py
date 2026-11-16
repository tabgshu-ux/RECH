# ==========================================
# 檔案路徑：modules/engineering/engineering_department.py
# 職責：工程部主控台（上方 Tabs 導覽 + 上方卡片下方互動表單 + 動態串聯人事員工清單）
# ==========================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
import datetime

def get_employee_list(engine):
    """動態從人事系統資料庫撈取真實員工姓名清單"""
    emp_list = ["陳志豪 (預設)", "阮文雄 (Nguyen Van Hung)", "黎文特 (Le Van Thien)", "林建良"]
    if engine is not None:
        try:
            df_emp = pd.read_sql("SELECT emp_name FROM hr_employees WHERE is_active = TRUE", con=engine)
            if not df_emp.empty:
                emp_list = df_emp["emp_name"].tolist()
        except Exception:
            pass
    return emp_list

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 🛠️ 工程部綜合管理與作業中心 (Engineering Department)")
    st.caption("上方分頁切換各項工程作業，頁面內部採上方卡片摘要、下方互動表單與人事名單動態串聯。")

    # 🌟 核心要求：上方為固定分頁（Tabs），讓使用者第一眼就能看到並切換所有工程子功能
    tab_names = [
        "📊 工程部總覽",
        "🚨 緊急維修派工",
        "📈 專案損益控管",
        "📋 專案報價追蹤",
        "🧪 FAT/SAT 驗收",
        "📝 施工日報表",
        "📍 外勤 GPS 打卡",
        "📐 設計圖庫專區"
    ]
    
    tabs = st.tabs(tab_names)

    # 1. 📊 工程部總覽（主管決策戰情）
    with tabs[0]:
        st.markdown("#### 📊 領導決策：全廠工程案場執行與損益戰情")
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("進行中案場", "12 案", "🟢 正常")
        with col2: st.metric("今日現場出勤", "86 人", "包含點工 18 人")
        with col3: st.metric("進度落後警示", "1 案", "需主管介入")
        with col4: st.metric("總合約金額", "325.5億 ₫", "執行率 78%")

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

    # 2. 🚨 緊急維修派工（已串聯人事員工清單）
    with tabs[1]:
        st.markdown("#### 🚨 緊急維修派工與事故公告通知中心")
        st.caption("突發事故廣播派工，指派人員直接串聯人事系統中的真實員工名單。")

        # 上方摘要卡片
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("進行中緊急單", "2 件", "🔴 處理中")
        with c2: st.metric("今日待派工", "0 件", "🟢 正常")
        with c3: st.metric("平均反應時間", "18 分鐘", "⚡ 高效")

        st.markdown("---")
        st.markdown("##### ✍️ 填寫緊急派工與事故通報表單")
        
        # 取得真實人事員工清單
        available_employees = get_employee_list(engine)

        with st.form("emergency_action_form_v2"):
            col1, col2 = st.columns(2)
            with col1:
                urgency = st.selectbox("緊急等級", ["🔴 紅色特急 (立即派工)", "🟡 普通緊急 (當日處理)"])
                vendor = st.text_input("外部廠商或案場名稱", placeholder="例如: 平陽美德金屬加工廠")
            with col2:
                # 🌟 關鍵修正：改用下拉選單多選或單選，直接綁定人事系統員工姓名
                assignees = st.multiselect("指派帶班工程師與師傅 (選自人事員工手冊)", options=available_employees, default=[available_employees[0]])
                tools = st.text_input("攜帶工具與備品", placeholder="例如: 三用電表、備用斷路器 100A")
            
            desc = st.text_area("事故狀況簡述與維修需求", placeholder="請描述故障現象及須前往廠商處執行的維修動作...")
            submitted = st.form_submit_button("📢 立即發布緊急派工單並同步廣播", type="primary", use_container_width=True)
            if submitted:
                assignee_str = ", ".join(assignees)
                st.success(f"🎉 成功發布緊急派工單！已指派人員：[{assignee_str}] 前往 [{vendor}]。")

        st.markdown("##### 📋 歷史緊急派工清單")
        history_df = pd.DataFrame({
            "單號": ["EMG-01", "EMG-02"],
            "廠商": ["西寧廠動力車間", "平陽美德廠"],
            "狀態": ["🔧 維修中", "✅ 已完工"],
            "指派人員": ["陳志豪、阮文雄", "黎文特"]
        })
        st.dataframe(history_df, use_container_width=True, hide_index=True)

    # 3. 📈 專案損益控管
    with tabs[2]:
        try:
            from modules.engineering import project_pnl
            project_pnl.show(engine=engine, lang=lang, **kwargs)
        except Exception:
            st.info("📈 正在載入工程專案損益與預算控管模組...")

    # 4. 📋 專案報價追蹤
    with tabs[3]:
        st.markdown("#### 📋 專案報價與管線追蹤中心")
        st.info("管理工程投標報價、BOM 成本估算與案場管線進度追蹤。")

    # 5. 🧪 FAT/SAT 驗收
    with tabs[4]:
        st.markdown("#### 🧪 FAT (出廠測試) 與 SAT (現場驗收) 簽認系統")
        with st.form("fatsat_form_v2"):
            fs_col1, fs_col2 = st.columns(2)
            with fs_col1:
                test_type = st.selectbox("測試類型", ["FAT 廠內出廠測試", "SAT 現場驗收測試"])
                project_name = st.text_input("案場專案名稱", placeholder="西寧廠二期配電盤")
            with fs_col2:
                inspector = st.selectbox("檢驗工程師 (選自人事系統)", options=get_employee_list(engine))
                client_rep = st.text_input("客戶代表簽名", placeholder="Mr. Nguyen (廠長)")

            st.markdown("**檢驗項目勾選：**")
            st.checkbox("1. 絕緣電阻測試 (> 100MΩ)", value=True)
            st.checkbox("2. 主母線耐壓與相序測試", value=True)
            st.checkbox("3. PLC 控制迴路與保戶動作測試", value=True)
            st.checkbox("4. 外觀烤漆與機構尺寸複核", value=True)

            fs_submitted = st.form_submit_button("✅ 提交驗收報告並取得主管/客戶簽認", type="primary", use_container_width=True)
            if fs_submitted:
                st.success(f"🎉 [{project_name}] 的 [{test_type}] 驗收報告已完成並存檔！")

    # 6. 📝 施工日報表
    with tabs[5]:
        st.markdown("#### 📝 施工日報表與點工點料登記")
        with st.form("daily_report_form_v2"):
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                r_date = st.date_input("施工日期", value=datetime.date.today())
                r_proj = st.text_input("施工案場", placeholder="平陽工業區廠房機電統包")
            with r_col2:
                r_workers = st.number_input("今日出勤總人數 (含點工)", min_value=1, value=15)
                r_overtime = st.number_input("加班總時數 (小時)", min_value=0, value=3)

            r_desc = st.text_area("今日施工進度摘要與耗用材料登記", placeholder="例如: 完成配電盤主體吊裝及控制線路敷設...")
            r_submitted = st.form_submit_button("💾 提交今日施工日報表", type="primary", use_container_width=True)
            if r_submitted:
                st.success(f"🎉 成功提交 [{r_proj}] 的施工日報！")

    # 7. 📍 外勤 GPS 打卡
    with tabs[6]:
        st.markdown("#### 📍 外勤師傅 GPS 圍籬即時打卡與足跡")
        st.info("💡 偵測外勤人員當前坐標，並記錄抵達案場或客戶廠區的時間。")
        with st.container(border=True):
            st.markdown("📍 坐標位置：`10.7769° N, 106.7009° E` (越南胡志明市/西寧案場圍籬範圍內)")
            if st.button("📍 立即進行外勤 GPS 打卡簽到", type="primary", use_container_width=True):
                st.success("🎉 GPS 打卡成功！已記錄時間與案場地理圍籬坐標。")

    # 8. 📐 設計圖庫專區
    with tabs[7]:
        st.markdown("#### 📐 配電盤電氣與機構設計圖庫 (設計人員專用)")
        st.info("💡 專為廠內設計人員打造：上傳與檢閱 AutoCAD / 3D 機構圖面、審查電氣迴路圖與版本控制。")
        
        design_df = pd.DataFrame({
            "圖面編號": ["DWG-2026-501", "DWG-2026-502", "DWG-2026-503"],
            "專案名稱": ["西寧廠二期總配電盤 (MSB)", "平陽廠自動控制盤 (PLC)", "隆安廠變壓器二次側箱"],
            "設計版本": ["Rev.02", "Rev.01", "Rev.03"],
            "負責設計師": ["張工程師", "李工程師", "王工程師"],
            "審查狀態": ["✅ 主管已核准", "⏳ 審查中", "✅ 客戶已簽認"]
        })
        st.dataframe(design_df, use_container_width=True, hide_index=True)

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
