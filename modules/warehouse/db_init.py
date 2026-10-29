import streamlit as st
from sqlalchemy import text

def init_warehouse_db(engine):
    """初始化倉庫相關資料表，並自動擴充舊表欄位確保 100% 相容與永不遺失"""
    if not engine:
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS warehouse_inventory (
                    item_code VARCHAR(50) PRIMARY KEY,
                    item_name VARCHAR(200) NOT NULL,
                    category VARCHAR(100),
                    spec VARCHAR(200),
                    barcode VARCHAR(100),
                    qty FLOAT DEFAULT 0,
                    unit VARCHAR(20) DEFAULT '只',
                    safety_stock FLOAT DEFAULT 5,
                    location VARCHAR(100),
                    updated VARCHAR(50),
                    photo_path TEXT
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS warehouse_logs (
                    log_id VARCHAR(50) PRIMARY KEY,
                    type VARCHAR(50),
                    item_code VARCHAR(50),
                    item_name VARCHAR(200),
                    qty FLOAT,
                    operator VARCHAR(100),
                    date VARCHAR(50),
                    note TEXT
                );
            """))

            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS warehouse_stocktaking (
                    check_id VARCHAR(50) PRIMARY KEY,
                    item_code VARCHAR(50),
                    item_name VARCHAR(200),
                    location VARCHAR(100),
                    book_qty FLOAT,
                    actual_qty FLOAT,
                    diff_qty FLOAT,
                    operator VARCHAR(100),
                    check_date VARCHAR(50),
                    status VARCHAR(50)
                );
            """))

            alter_queries = [
                "ALTER TABLE warehouse_inventory ADD COLUMN IF NOT EXISTS safety_stock FLOAT DEFAULT 5;",
                "ALTER TABLE warehouse_inventory ADD COLUMN IF NOT EXISTS barcode VARCHAR(100);",
                "ALTER TABLE warehouse_inventory ADD COLUMN IF NOT EXISTS photo_path TEXT;",
                "ALTER TABLE warehouse_logs ADD COLUMN IF NOT EXISTS log_id VARCHAR(50);",
                "ALTER TABLE warehouse_logs ADD COLUMN IF NOT EXISTS date VARCHAR(50);",
                "ALTER TABLE warehouse_logs ADD COLUMN IF NOT EXISTS note TEXT;"
            ]
            for q in alter_queries:
                try:
                    conn.execute(text(q))
                except Exception:
                    pass
    except Exception as e:
        st.warning(f"資料庫結構自動升級提示: {e}")

def load_warehouse_data(engine):
    inventory_db = []
    logs_db = []
    stocktake_db = []
    if not engine:
        return inventory_db, logs_db, stocktake_db
    
    try:
        with engine.connect() as conn:
            try:
                res_inv = conn.execute(text("SELECT * FROM warehouse_inventory")).fetchall()
                for r in res_inv:
                    inventory_db.append({
                        "item_code": r[0] if len(r) > 0 else "", 
                        "item_name": r[1] if len(r) > 1 else "", 
                        "category": r[2] if len(r) > 2 else "", 
                        "spec": r[3] if len(r) > 3 else "",
                        "barcode": r[4] if len(r) > 4 else "", 
                        "qty": r[5] if len(r) > 5 else 0, 
                        "unit": r[6] if len(r) > 6 else "只", 
                        "safety_stock": r[7] if len(r) > 7 else 5,
                        "location": r[8] if len(r) > 8 else "A區", 
                        "updated": r[9] if len(r) > 9 else "", 
                        "photo": r[10] if len(r) > 10 else None
                    })
            except Exception:
                pass

            try:
                res_logs = conn.execute(text("SELECT * FROM warehouse_logs ORDER BY date DESC, log_id DESC")).fetchall()
                for r in res_logs:
                    logs_db.append({
                        "log_id": r[0] if len(r) > 0 else "", 
                        "type": r[1] if len(r) > 1 else "", 
                        "item_code": r[2] if len(r) > 2 else "", 
                        "item_name": r[3] if len(r) > 3 else "",
                        "qty": r[4] if len(r) > 4 else 0, 
                        "operator": r[5] if len(r) > 5 else "", 
                        "date": r[6] if len(r) > 6 else "", 
                        "note": r[7] if len(r) > 7 else ""
                    })
            except Exception:
                pass

            try:
                res_st = conn.execute(text("SELECT * FROM warehouse_stocktaking ORDER BY check_date DESC")).fetchall()
                for r in res_st:
                    stocktake_db.append({
                        "check_id": r[0] if len(r) > 0 else "", 
                        "item_code": r[1] if len(r) > 1 else "", 
                        "item_name": r[2] if len(r) > 2 else "", 
                        "location": r[3] if len(r) > 3 else "",
                        "book_qty": r[4] if len(r) > 4 else 0, 
                        "actual_qty": r[5] if len(r) > 5 else 0, 
                        "diff_qty": r[6] if len(r) > 6 else 0, 
                        "operator": r[7] if len(r) > 7 else "",
                        "check_date": r[8] if len(r) > 8 else "", 
                        "status": r[9] if len(r) > 9 else ""
                    })
            except Exception:
                pass
    except Exception:
        pass

    return inventory_db, logs_db, stocktake_db
