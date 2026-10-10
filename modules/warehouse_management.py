-- 1. 建立倉庫庫存資料表
CREATE TABLE IF NOT EXISTS warehouse_inventory (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    warehouse VARCHAR(100),
    qty NUMERIC(12, 2) DEFAULT 0.0,
    safety NUMERIC(12, 2) DEFAULT 0.0,
    status VARCHAR(50) DEFAULT '庫存充足',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 建立倉庫出入庫與領料歷史日誌表
CREATE TABLE IF NOT EXISTS warehouse_logs (
    id SERIAL PRIMARY KEY,
    op_time VARCHAR(50),
    op_type VARCHAR(50),
    code VARCHAR(100),
    name VARCHAR(255),
    warehouse VARCHAR(100),
    qty NUMERIC(12, 2),
    receiver_or_supplier VARCHAR(255),
    staff VARCHAR(255),
    memo TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
