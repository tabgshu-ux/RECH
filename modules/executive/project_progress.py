import streamlit as st
import pandas as pd

def render_project_progress_page(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### ⚡ 工程專案進度與現場異常紅綠燈監控")
    st.caption("即時掌握各廠區在手專案合約、目前施工階段（談判中、等待開標、設備安裝、驗收中）與現場回報異常。")

    # 工程專案進度與異常監控資料表
    proj_exec_data = [
        {
            "專案代碼": "HD-2025-HOT", 
            "客戶名稱": "和廓隆建築 (Ho Team)", 
            "廠區": "西寧廠", 
            "專案合約總額": "45,000,000,000 ₫", 
            "專案進度": "85% (設備安裝中)", 
            "現場回報與異常狀態": "🟢 正常施工, 預計下週進行無載試車", 
            "負責人": "李佑銘"
        },
        {
            "專案代碼": "HD-2026-JIA", 
            "客戶名稱": "佳威商旅", 
            "廠區": "海防廠", 
            "專案合約總額": "28,500,000,000 ₫", 
            "專案進度": "30% (過路橋架配管)", 
            "現場回報與異常狀態": "🔴 現場土木機電延遲 3 天，已指派工務經理協調外包商", 
            "負責人": "阮文強"
        },
        {
            "專案代碼": "HD-2026-YAN", 
            "客戶名稱": "彥豪金屬工業", 
            "廠區": "西寧廠", 
            "專案合約總額": "41,900,000,000 ₫", 
            "專案進度": "50% (配電盤出廠複檢)", 
            "現場回報與異常狀態": "🟢 銅排母線檢驗合格, 等待客戶驗收", 
            "負責人": "陳經理"
        }
    ]
    st.dataframe(pd.DataFrame(proj_exec_data), use_container_width=True)
    
    st.info("💡 **專案進度生命週期備註**：系統會自動追蹤從『專案接洽 ➡️ 審標開標 ➡️ 廠內板金與配盤 ➡️ 現場安裝 ➡️ 初驗與正式驗收』的全生命週期狀態，若有紅燈異常將自動通報總經理室與工務主管。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_project_progress_page(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_project_progress_page(engine=engine, lang=lang, **kwargs)
