from sqlalchemy import create_engine, Column, String, Integer, DateTime, Numeric, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BookingModel(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False)
    customer_name = Column(String(100))
    booking_date_info = Column(Text)
    transcript = Column(Text)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum('pending', 'confirmed', 'cancelled', 'failed', name='booking_status'), default='pending')
    upi_txn_id = Column(String(100), unique=True)
    receipt_ocr_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()