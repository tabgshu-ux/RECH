import os
import streamlit as st
from sqlalchemy import create_engine

def get_db_engine(passed_engine=None):
    """精準對應您現有 Secrets 的 SUPABASE_DB_URL 連線函式"""
    if passed_engine is not None:
        return passed_engine
        
    db_url = None
    
    # 1. 優先從 st.secrets 讀取 SUPABASE_DB_URL
    try:
        if "SUPABASE_DB_URL" in st.secrets:
            db_url = st.secrets["SUPABASE_DB_URL"]
    except Exception:
        pass
        
    # 2. 備援：嘗試從舊的巢狀結構或環境變數讀取
    if not db_url:
        try:
            if "database" in st.secrets and "url" in st.secrets["database"]:
                db_url = st.secrets["database"]["url"]
        except Exception:
            pass
            
    if not db_url:
        db_url = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
        
    if db_url:
        try:
            return create_engine(db_url)
        except Exception as e:
            st.error(f"⚠️ 建立資料庫引擎發生異常: {e}")
            return None
            
    return None
