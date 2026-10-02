from contextlib import contextmanager
from sqlalchemy import create_engine, text
import streamlit as st

# 使用 Supabase 5432 埠，並設定嚴格的池控管與逾時自動回收
DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:Reetech2026@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres?sslmode=require"

@st.cache_resource
def get_db_engine():
    """建立安全的單例資料庫引擎，限制 pool_size 避免爆連線"""
    try:
        eng = create_engine(
            DB_URL,
            pool_pre_ping=True,
            pool_size=2,        # 嚴格限制核心連線數
            max_overflow=3,     # 允許最大溢出數
            pool_recycle=30,    # 30秒自動回收閒置連線
            connect_args={"connect_timeout": 5}
        )
        return eng
    except Exception as e:
        print(f"DB Engine Init Error: {e}")
        return None

@contextmanager
def get_db_connection():
    """安全取得資料庫連線的 Context Manager，用完立刻自動釋放"""
    engine = get_db_engine()
    if not engine:
        yield None
        return
    
    conn = engine.connect()
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()  # 💡 確保連線一定會被關閉，釋放額度！
