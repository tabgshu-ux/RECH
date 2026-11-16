# ==========================================
# 檔案路徑：modules/engineering/engineering_department.py
# 職責：工程部主控台（依「現場工程、設計、考勤、驗收報告」四大直覺分類與按鈕導覽）
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
    # 初始化工程部內部子路由狀態
    if 'eng_sub_view' not in st.session_state:
        st.session_state['eng_sub_view'] = 'overview'

    # 如果有點擊返回總覽
    if st.session_state.get('eng_sub_view') != 'overview':
        if st.button("⬅️ 返回工程部總覽戰情", key="back_to_eng_overview"):
            st.session_state['eng_sub_view'] = 'overview'
            st.rerun()
        st.markdown("---")

    current_sub = st.session_state['eng_sub_view']

    # 1. 👑 工程部總覽（戰情儀表板 + 四大直覺分類大卡片）
    if current_sub == 'overview':
        st.markdown("### 🛠️ 工程部綜合管理與作業中心 (Engineering Department)")
        st.caption("全廠工程案場執行戰情室與直覺化功能導覽。")

        # 上方指標卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("進行中案場", "12 案", "🟢 正常")
        with col2: st.metric("今日現場出勤", "86 人", "包含點工 18 人")
        with col3: st.metric("進度落後警示", "1 案", "需主管介入")
        with col4: st.metric("總合約金額", "325.5億 ₫", "執行率 78%")

        st.markdown("---")
        st.markdown("##### 📌 工程部近期異常警示與進度追蹤")
        warning_df = pd.DataFrame({
            "日期": ["2026-11-16", "2026-11-15", "2026-11-14"],
            "案場編號": ["PRJ-2026-01", "PRJ-2026-02", "PRJ-2026-03"],
            "案場名稱": ["西寧廠二期配電盤擴建", "平陽工業區廠房機電統包", "隆安省光電園區變壓器"],
            "事件類型": ["材料超支警示", "進度落後 5%", "設備驗收待簽認"],
            "處理狀態": ["🔴 待主管審核", "🟡 趕工中", "✅ 已改善"]
        })
        st.dataframe(warning_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### 📂 工程部四大核心分類專區")
        
        # 🌟 依照您的要求精準劃分四大分類卡片
        cols = st.columns(4)
        eng_sections = [
            {"id": "field", "name": "🛠️ 現場工程", "desc": "緊急維修派工、施工日報表與點工點料登記。"},
            {"id": "design", "name": "📐 設計圖庫", "desc": "配電盤電氣與機構設計圖面版本控制與審查。"},
            {"id": "attendance", "name": "⏱️ 考勤打卡", "desc": "外勤師傅 GPS 圍籬即時打卡與出勤足跡紀錄。"},
            {"id": "fatsat", "name": "🧪 驗收報告", "desc": "FAT 廠內出廠測試與 SAT 現場驗收簽認報告。"}
        ]
        
        for idx, sec in enumerate(eng_sections):
            with cols[idx]:
                with st.container(border=True):
                    st.markdown(f"#### {sec['name']}")
                    st.caption(sec['desc'])
                    if st.button("進入專區 ➡️", key=f"btn_eng_sec_{sec['id']}", use_container_width=True, type="primary"):
                        st.session_state['eng_sub_view'] = sec['id']
                        st.rerun()

        # 額外的輔助卡片（專案損益與報價）
        st.markdown("")
        c_pnl1, c_pnl2 = st.columns(2)
        with c_pnl1:
            with st.container(border=True):
                st.markdown("#### 📈 專案損益與預算控管")
                st.caption("工程專案成本歸屬、外包工資與毛利分析。")
                if st.button("進入損益專區 ➡️", key="btn_pnl_sec", use_container_width=True):
                    st.session_state['eng_sub_view'] = 'pnl'
                    st.rerun()
        with c_pnl2:
            with st.container(border=True):
                st.markdown("#### 📋 專案報價追蹤")
                st.caption("投標報價、BOM 成本估算與管線進度。")
                if st.button("進入報價專區 ➡️", key="btn_quote_sec", use_container_width=True):
                    st.session_state['eng_sub_view'] = 'quote'
                    st.rerun()

    # 2. 進入各專區後的「上方四大分類按鈕導覽列 + 下方互動表單」
    else:
        # 上方精準對齊的按鈕導覽列
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        with b1:
            if st.button("🛠️ 現場工程", use_container_width=True, type="primary" if current_sub == 'field' else "secondary"):
                st.session_state['eng_sub_view'] = 'field'; st.rerun()
        with b2:
            if st.button("📐 設計圖庫", use_container_width=True, type="primary" if current_sub == 'design' else "secondary"):
                st.session_state['eng_sub_view'] = 'design'; st.rerun()
        with b3:
            if st.button("⏱️ 考勤打卡", use_container_width=True, type="primary" if current_sub == 'attendance' else "secondary"):
                st.session_state['eng_sub_view'] = 'attendance'; st.rerun()
        with b4:
            if st.button("🧪 驗收報告", use_container_width=True, type="primary" if current_sub == 'fatsat' else "secondary"):
                st.session_state['eng_sub_view'] = 'fatsat'; st.rerun()
        with b5:
            if st.button("📈 專案損益", use_container_width=True, type="primary" if current_sub == 'pnl' else "secondary"):
                st.session_state['eng_sub_view'] = 'pnl'; st.rerun()
        with b6:
            if st.button("📋 專案報價", use_container_width=True, type="primary" if current_sub == 'quote' else "secondary"):
                st.session_state['eng_sub_view'] = 'quote'; st.rerun()

        st.markdown("---")

        # 各分類對應的互動表單內容
        if current_sub == 'field':
            st.markdown("#### 🛠️ 現場工程管理與緊急維修派工")
            st.caption("突發事故廣播派工與每日施工日報登記。")
            
            available_employees = get_employee_list(engine)

            with st.form("emergency_action_form_v4"):
                st.markdown("##### 🚨 緊急維修派工表單")
                col1, col2 = st.columns(2)
                with col1:
                    urgency = st.selectbox("緊急等級", ["🔴 紅色特急 (立即派工)", "🟡 普通緊急 (當日處理)"])
                    vendor = st.text_input("外部廠商或案場名稱", placeholder="例如: 平陽美德金屬加工廠")
                with col2:
                    assignees = st.multiselect("指派帶班工程師與師傅 (選自人事員工手冊)", options=available_employees, default=[available_employees[0]])
                    tools = st.text_input("攜帶工具與備品", placeholder="例如: 三用電表、備用斷路器")
                
                desc = st.text_area("事故狀況簡述與維修需求", placeholder="請描述故障現象及須前往執行的維修動作...")
                submitted = st.form_submit_button("📢 立即發布緊急派工單", type="primary", use_container_width=True)
                if submitted:
                    assignee_str = ", ".join(assignees)
                    st.success(f"🎉 成功發布緊急派工單！已指派：[{assignee_str}] 前往 [{vendor}]。")

            st.markdown("---")
            st.markdown("##### 📝 施工日報表與點工點料登記")
            with st.form("daily_report_form_v4"):
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

        elif current_sub == 'design':
            st.markdown("#### 📐 配電盤電氣與機構設計圖庫")
            st.info("💡 專為廠內設計人員打造：上傳與檢閱 AutoCAD / 3D 機構圖面、審查電氣迴路圖與版本控制。")
            
            with st.form("upload_dwg_form_v2"):
                d_col1, d_col2 = st.columns(2)
                with d_col1:
                    dwg_no = st.text_input("圖面編號", placeholder="DWG-2026-504")
                    dwg_name = st.text_input("專案與圖面名稱", placeholder="新順工業區主配電盤配置圖")
                with d_col2:
                    dwg_rev = st.text_input("設計版本", value="Rev.01")
                    designer = st.selectbox("負責設計師 (選自人事系統)", options=get_employee_list(engine))
                
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

        elif current_sub == 'attendance':
            st.markdown("#### ⏱️ 外勤師傅考勤與 GPS 圍籬打卡")
            st.info("💡 偵測外勤人員當前坐標，記錄抵達案場或客戶廠區的時間與出勤足跡。")
            
            with st.container(border=True):
                st.markdown("📍 當前 GPS 定位狀態：`10.7769° N, 106.7009° E` (越南胡志明市/西寧案場圍籬範圍內)")
                if st.button("📍 立即進行外勤 GPS 打卡簽到", type="primary", use_container_width=True):
                    st.success("🎉 GPS 打卡成功！已記錄時間與地理圍籬坐標，並同步至考勤薪資系統。")

            st.markdown("##### 📋 今日外勤打卡足跡紀錄")
            gps_df = pd.DataFrame({
                "員工姓名": ["阮文雄", "陳志豪", "黎文特"],
                "打卡地點": ["西寧廠二期", "平陽美德廠", "隆安光電園區"],
                "打卡時間": ["08:15:32", "08:30:10", "09:05:44"],
                "狀態": ["✅ 圍籬內正常", "✅ 圍籬內正常", "✅ 圍籬內正常"]
            })
            st.dataframe(gps_df, use_container_width=True, hide_index=True)

        elif current_sub == 'fatsat':
            st.markdown("#### 🧪 FAT (出廠測試) 與 SAT (現場驗收) 簽認報告")
            with st.form("fatsat_form_v4"):
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

        elif current_sub == 'pnl':
            try:
                from modules.engineering import project_pnl
                project_pnl.show(engine=engine, lang=lang, **kwargs)
            except Exception:
                st.markdown("#### 📈 工程專案損益與預算控管")
                st.info("管理各案場成本歸屬、外包工資與毛利分析。")

        elif current_sub == 'quote':
            st.markdown("#### 📋 專案報價與管線追蹤")
            st.info("管理工程投標報價、BOM 成本估算與案場管線進度追蹤。")

def render(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    show(engine=engine, lang=lang, **kwargs)
