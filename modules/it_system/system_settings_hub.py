import streamlit as st

def show(engine=None, lang="繁體中文", **kwargs):
    st.markdown("### 💻 系統核心設定中心 (System Settings Hub)")
    
    # 建立系統設定的獨立子分頁，各自呼叫獨立的模組檔案
    tab1, tab2 = st.tabs(["🏢 部門與自動模組掛載", "🎨 企業品牌與識別 (Logo)"])
    
    with tab1:
        from modules.it_system import department_config
        department_config.render(engine=engine, lang=lang, **kwargs)
        
    with tab2:
        from modules.it_system import branding_config
        branding_config.render(engine=engine, lang=lang, **kwargs)
