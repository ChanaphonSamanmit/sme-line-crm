-- ═══════════════════════════════════════════════════════════
--  Author: Chanaphon Samanmit (Backend Lead)
-- ═══════════════════════════════════════════════════════════

--  ตาราง: สินค้า 
CREATE TABLE products (
    id          UUID    DEFAULT gen_random_uuid() PRIMARY KEY,
    merchant_id UUID    NOT NULL,
    name        TEXT    NOT NULL,
    price       NUMERIC(10,2) NOT NULL,
    cost_price  NUMERIC(10,2) DEFAULT 0,
    image_url   TEXT    DEFAULT '',
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

--  ตาราง: สมาชิก (ลูกค้าที่มี LINE)
CREATE TABLE members (
    id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    merchant_id  UUID NOT NULL,
    line_user_id TEXT NOT NULL,
    display_name TEXT NOT NULL,
    picture_url  TEXT DEFAULT '',
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (merchant_id, line_user_id)
);

-- ตาราง: รายการซื้อ (ใบเสร็จ)
CREATE TABLE member_transactions (
    id               UUID    DEFAULT gen_random_uuid() PRIMARY KEY,
    merchant_id      UUID    NOT NULL,
    line_user_id     TEXT,
    amount           NUMERIC(10,2) NOT NULL,
    discount_applied NUMERIC(10,2) DEFAULT 0,
    receipt_id       TEXT    DEFAULT 'AUTO',
    status           TEXT    DEFAULT 'pending',  -- 'pending' | 'claimed'
    customer_name    TEXT,
    customer_picture TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ตาราง: รายการสินค้าในใบเสร็จ
CREATE TABLE transaction_items (
    id             UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    transaction_id UUID REFERENCES member_transactions(id) ON DELETE CASCADE,
    product_id     UUID REFERENCES products(id),
    quantity       INT  NOT NULL DEFAULT 1,
    price_at_sale  NUMERIC(10,2) NOT NULL,
    cost_at_sale   NUMERIC(10,2) DEFAULT 0
);

CREATE INDEX idx_transactions_merchant  ON member_transactions(merchant_id);
CREATE INDEX idx_transactions_line_user ON member_transactions(line_user_id);
CREATE INDEX idx_products_merchant      ON products(merchant_id);
CREATE INDEX idx_members_merchant_line  ON members(merchant_id, line_user_id);
