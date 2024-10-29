# fox_scraper/core/database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class DataSource(Base):
    __tablename__ = 'data_sources'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text)
    config = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scraping_runs = relationship("ScrapingRun", back_populates="source")
    raw_data = relationship("RawData", back_populates="source")

class ScrapingRun(Base):
    __tablename__ = 'scraping_runs'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('data_sources.id'))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(50))
    items_processed = Column(Integer, default=0)
    errors = Column(JSONB)
    stats = Column(JSONB)
    config_snapshot = Column(JSONB)

    # Relationships
    source = relationship("DataSource", back_populates="scraping_runs")
    raw_data = relationship("RawData", back_populates="run")

class RawData(Base):
    __tablename__ = 'raw_data'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('data_sources.id'))
    run_id = Column(Integer, ForeignKey('scraping_runs.id'))
    url = Column(Text)
    raw_content = Column(JSONB)
    hash = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    processing_status = Column(String(50), default='pending')

    # Relationships
    source = relationship("DataSource", back_populates="raw_data")
    run = relationship("ScrapingRun", back_populates="raw_data")
    cleaned_data = relationship("CleanedData", back_populates="raw_data")

class CleanedData(Base):
    __tablename__ = 'cleaned_data'

    id = Column(Integer, primary_key=True)
    raw_data_id = Column(Integer, ForeignKey('raw_data.id'))
    source_id = Column(Integer, ForeignKey('data_sources.id'))
    name = Column(String(255))
    category = Column(String(255))
    address = Column(JSONB)
    contact = Column(JSONB)
    data_json = Column(JSONB)
    cleaned_at = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(String(50))
    validation_errors = Column(JSONB)

    # Relationships
    raw_data = relationship("RawData", back_populates="cleaned_data")
    enriched_data = relationship("EnrichedData", back_populates="cleaned_data")

class EnrichedData(Base):
    __tablename__ = 'enriched_data'

    id = Column(Integer, primary_key=True)
    cleaned_data_id = Column(Integer, ForeignKey('cleaned_data.id'))
    enrichment_type = Column(String(255))
    data = Column(JSONB)
    source = Column(String(255))
    enriched_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)

    # Relationships
    cleaned_data = relationship("CleanedData", back_populates="enriched_data")

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.Session = None
        self.setup_connection()

    def setup_connection(self):
        db_config = {
            'host': os.getenv('DB_HOST', '192.168.1.164'),
            'database': os.getenv('DB_NAME', 'fox_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'Milena84'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        connection_string = (
            f"postgresql://{db_config['user']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()