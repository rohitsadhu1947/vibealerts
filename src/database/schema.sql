-- Stock symbols master table
CREATE TABLE IF NOT EXISTS stock_symbols (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(200),
    isin VARCHAR(12),
    sector VARCHAR(100),
    market_cap_cr DECIMAL(15, 2),
    is_nifty50 BOOLEAN DEFAULT false,
    is_nifty500 BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_symbols_symbol ON stock_symbols(symbol);

-- Analyst estimates
CREATE TABLE IF NOT EXISTS analyst_estimates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    fiscal_year INTEGER NOT NULL,
    revenue_est DECIMAL(15, 2),
    profit_est DECIMAL(15, 2),
    eps_est DECIMAL(10, 2),
    ebitda_est DECIMAL(15, 2),
    source VARCHAR(50),
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, quarter, fiscal_year)
);

CREATE INDEX IF NOT EXISTS idx_estimates_symbol ON analyst_estimates(symbol);

-- Quarterly results (actual)
CREATE TABLE IF NOT EXISTS quarterly_results (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    fiscal_year INTEGER NOT NULL,
    revenue DECIMAL(15, 2),
    profit_after_tax DECIMAL(15, 2),
    eps DECIMAL(10, 2),
    ebitda DECIMAL(15, 2),
    operating_profit DECIMAL(15, 2),
    total_income DECIMAL(15, 2),
    revenue_prev_quarter DECIMAL(15, 2),
    profit_prev_quarter DECIMAL(15, 2),
    revenue_prev_year DECIMAL(15, 2),
    profit_prev_year DECIMAL(15, 2),
    yoy_revenue_growth DECIMAL(6, 2),
    yoy_profit_growth DECIMAL(6, 2),
    qoq_revenue_growth DECIMAL(6, 2),
    qoq_profit_growth DECIMAL(6, 2),
    revenue_beat_pct DECIMAL(6, 2),
    profit_beat_pct DECIMAL(6, 2),
    eps_beat_pct DECIMAL(6, 2),
    sentiment VARCHAR(20),
    sentiment_score DECIMAL(6, 2),
    pdf_url TEXT,
    extraction_method VARCHAR(50),
    confidence_score DECIMAL(3, 2),
    extraction_time_ms INTEGER,
    announced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, quarter, fiscal_year)
);

CREATE INDEX IF NOT EXISTS idx_results_symbol ON quarterly_results(symbol);
CREATE INDEX IF NOT EXISTS idx_results_announced ON quarterly_results(announced_at DESC);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    telegram_chat_id BIGINT NOT NULL,
    username VARCHAR(100),
    is_premium BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    joined_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(user_id);

-- User watchlists
CREATE TABLE IF NOT EXISTS user_watchlists (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    added_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, symbol)
);

CREATE INDEX IF NOT EXISTS idx_watchlists_user ON user_watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlists_symbol ON user_watchlists(symbol) WHERE enabled = true;

-- Alerts sent log
CREATE TABLE IF NOT EXISTS alerts_sent (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    quarter INTEGER,
    fiscal_year INTEGER,
    sentiment VARCHAR(20),
    detection_time_sec DECIMAL(6, 2),
    telegram_message_id BIGINT,
    channel_delivered BOOLEAN DEFAULT true,
    dm_delivered_count INTEGER DEFAULT 0,
    sent_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_sent_at ON alerts_sent(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts_sent(symbol);

-- Processing errors log
CREATE TABLE IF NOT EXISTS processing_errors (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    error_type VARCHAR(50),
    error_message TEXT,
    stack_trace TEXT,
    context JSONB,
    occurred_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_errors_occurred ON processing_errors(occurred_at DESC);

