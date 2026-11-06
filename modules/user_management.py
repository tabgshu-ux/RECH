import streamlit as st
import pandas as pd
from sqlalchemy import text

def render_user_management(engine=None, lang="繁體中文", **kwargs):
    st.title("👥 員工檔案與人事帳號管理")
    st.caption("管理公司內部員工的基本資料與系統存取帳號。")
    st.markdown("---")
    
    # 這裡專注於員工與人事資料的維護
    st.info("💡 此模組專注於員工檔案管理。系統設定與部門掛載請至【資訊管理部 (IT & System)】進行配置。")

def show(engine=None, lang="繁體中文", **kwargs):
    render_user_management(engine=engine, lang=lang, **kwargs)

def main(engine=None, lang="繁體中文", **kwargs):
    render_user_management(engine=engine, lang=lang, **kwargs)
