import streamlit as st
import pandas as pd

def render_project_progress_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### ⚡ 工程專案進度與現場狀態追蹤")
    st.caption("監控各廠區在手專案之合約金額、施工進度與現場回報狀態。")

    proj_exec_data = [
        {"專案代碼": "HD-2025-HOT", "客戶名稱": "和廓隆建築", "廠區": "西寧廠", "合約總額": "45,000,000,000 ₫", "進度": "85% (設備安裝)", "現場狀態": "正常施工，排定無載試車", "負責人": "李佑銘"},
        {"專案代碼": "HD-2026-JIA", "客戶名稱": "佳威商旅", "廠區": "海防廠", "合約總額": "28,500,000,000 ₫", "進度": "30% (橋架配管)", "現場狀態": "工序延遲三日，協調外包商中", "負責人": "阮文強"},
        {"專案代碼": "HD-2026-YAN", "客戶名稱": "彥豪金屬工業", "廠區": "西寧廠", "合約總額": "41,900,000,000 ₫", "進度": "50% (出廠複檢)", "現場狀態": "母線檢驗合格，待客戶驗收", "負責人": "陳經理"}
    ]
    st.dataframe(pd.DataFrame(proj_exec_data), use_container_width=True)
    st.info("註：專案生命週期包含合約洽談、審標、廠內製造、現場安裝與正式驗收。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_project_progress_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_project_progress_page(engine=engine, lang=lang, **kwargs)
