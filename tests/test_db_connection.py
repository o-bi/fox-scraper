# test_db_connection.py
import psycopg2
import logging

def test_connection():
    try:
        # Connect to local PostgreSQL
        conn = psycopg2.connect(
            host="192.168.1.164",
            database="fox_db",
            user="postgres",
            password="Milena84",
            port="5432"
        )
        
        cur = conn.cursor()
        
        # Create the table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS collect_ortliche_vet (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                content TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_collect_ortliche_vet_url 
                ON collect_ortliche_vet(url);
        """)
        conn.commit()
        
        # Get current count
        cur.execute("SELECT COUNT(*) FROM collect_ortliche_vet")
        count = cur.fetchone()[0]
        print(f"Successfully connected to database! Current record count: {count}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()