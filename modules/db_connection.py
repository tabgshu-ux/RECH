from contextlib import contextmanager
from sqlalchemy import create_engine, text
import streamlit as st

DB_URL = "postgresql+psycopg2://postgres.wvsqbefyeykmueffcbwd:Reetech2026@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres?sslmode=require"

@st.cache_resource
def get_db_engine():
    """建立安全的單例資料庫引擎"""
    try:
        eng = create_engine(
            DB_URL,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=3,
            pool_recycle=30,
            connect_args={"connect_timeout": 5}
        )
        return eng
    except Exception as e:
        print(f"DB Engine Init Error: {e}")
        return None

@contextmanager
def get_db_connection():
    """安全取得資料庫連線的 Context Manager"""
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
        conn.close()

# 🛡️ 額外防護：如果有些模組誤把 engine 當成字串呼叫，提供安全轉換
def ensure_engine(engine_or_url):
    if engine_or_url is None:
        return get_db_engine()
    if isinstance(engine_or_url, str):
        try:
            return create_engine(engine_or_url)
        except Exception:
            return get_db_engine()
    return engine_or_url
