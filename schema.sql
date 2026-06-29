-- PostgreSQL Schema for Zero-Cost Booking System

-- Extension for UUID generation if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Status Enum
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'cancelled', 'failed');

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone VARCHAR(20) NOT NULL,
    customer_name VARCHAR(100),
    booking_date_info TEXT, -- Store the raw time info from voice
    transcript TEXT,        -- Store the full voice transcript
    amount DECIMAL(10, 2) NOT NULL,
    status booking_status DEFAULT 'pending',
    upi_txn_id VARCHAR(100) UNIQUE,
    receipt_ocr_text TEXT,  -- Store the OCR result for audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups by phone and status
CREATE INDEX idx_bookings_phone ON bookings(phone);
CREATE INDEX idx_bookings_status ON bookings(status);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();