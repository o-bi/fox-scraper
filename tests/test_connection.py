# test_connection.py
import asyncio
import psycopg2
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

def test_direct_connection():
    """Test direct PostgreSQL connection"""
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    result = urlparse(db_url)
    
    # Convert connection string to parameters
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    try:
        conn = psycopg2.connect(
            database=database,
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        print("Database connection successful!")
        
        # Try to create the table directly
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS website_data (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("Table created successfully!")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    test_direct_connection()