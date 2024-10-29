# fox_scraper/maintenance/db_reset.py
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def reset_database():
    load_dotenv()
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', '192.168.1.164'),
        'database': os.getenv('DB_NAME', 'fox_db'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'Milena84'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    # Create connection string
    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )
    
    # Create engine
    engine = create_engine(connection_string)
    
    try:
        # Connect and execute SQL
        with engine.connect() as connection:
            # List of SQL statements to execute
            sql_statements = [
                # Drop existing tables
                """DROP TABLE IF EXISTS collect_ortliche_vet CASCADE;""",
                
                # Create data_sources table
                """
                CREATE TABLE data_sources (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    config JSONB,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
                """,
                
                # Create scraping_runs table
                """
                CREATE TABLE scraping_runs (
                    id SERIAL PRIMARY KEY,
                    source_id INTEGER REFERENCES data_sources(id),
                    start_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMPTZ,
                    status VARCHAR(50),
                    items_processed INTEGER DEFAULT 0,
                    errors JSONB,
                    stats JSONB,
                    config_snapshot JSONB
                );
                """,
                
                # Create raw_data table
                """
                CREATE TABLE raw_data (
                    id SERIAL PRIMARY KEY,
                    source_id INTEGER REFERENCES data_sources(id),
                    run_id INTEGER REFERENCES scraping_runs(id),
                    url TEXT,
                    raw_content JSONB,
                    hash TEXT,
                    scraped_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    processing_status VARCHAR(50) DEFAULT 'pending'
                );
                """,
                
                # Create cleaned_data table
                """
                CREATE TABLE cleaned_data (
                    id SERIAL PRIMARY KEY,
                    raw_data_id INTEGER REFERENCES raw_data(id),
                    source_id INTEGER REFERENCES data_sources(id),
                    name VARCHAR(255),
                    category VARCHAR(255),
                    address JSONB,
                    contact JSONB,
                    data_json JSONB,
                    cleaned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    validation_status VARCHAR(50),
                    validation_errors JSONB
                );
                """,
                
                # Create enriched_data table
                """
                CREATE TABLE enriched_data (
                    id SERIAL PRIMARY KEY,
                    cleaned_data_id INTEGER REFERENCES cleaned_data(id),
                    enrichment_type VARCHAR(255),
                    data JSONB,
                    source VARCHAR(255),
                    enriched_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    confidence_score FLOAT
                );
                """,
                
                # Create master_records table
                """
                CREATE TABLE master_records (
                    id SERIAL PRIMARY KEY,
                    external_id VARCHAR(255),
                    name VARCHAR(255),
                    type VARCHAR(255),
                    status VARCHAR(50),
                    primary_data JSONB,
                    address JSONB,
                    contact JSONB,
                    data_json JSONB,
                    sources JSONB,
                    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    confidence_score FLOAT
                );
                """,
                
                # Create indexes
                """
                CREATE INDEX idx_raw_data_hash ON raw_data(hash);
                CREATE INDEX idx_raw_data_status ON raw_data(processing_status);
                CREATE INDEX idx_cleaned_data_validation ON cleaned_data(validation_status);
                CREATE INDEX idx_master_records_external_id ON master_records(external_id);
                CREATE INDEX idx_master_records_name ON master_records(name);
                CREATE INDEX idx_raw_data_content ON raw_data USING gin (raw_content);
                CREATE INDEX idx_master_records_data ON master_records USING gin (data_json);
                """
            ]
            
            # Execute each statement
            for statement in sql_statements:
                connection.execute(text(statement))
                connection.commit()
                
        print("Database reset and initialized successfully!")
        
    except Exception as e:
        print(f"Error resetting database: {str(e)}")

if __name__ == "__main__":
    reset_database()