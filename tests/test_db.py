# test_db.py
import psycopg2
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

def test_database():
    load_dotenv()
    
    try:
        # Connect to database
        db_url = os.getenv('DATABASE_URL')
        result = urlparse(db_url)
        
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cur = conn.cursor()
        
        # Get count of records
        cur.execute("SELECT COUNT(*) FROM collect_ortliche_vet;")
        count = cur.fetchone()[0]
        print(f"\nTotal records in database: {count}")
        
        # Get sample of records
        if count > 0:
            cur.execute("""
                SELECT id, title, url, 
                       metadata->'address'->>'street' as street,
                       metadata->'address'->>'city' as city
                FROM collect_ortliche_vet 
                LIMIT 5;
            """)
            
            print("\nSample records:")
            for record in cur.fetchall():
                print(f"\nID: {record[0]}")
                print(f"Title: {record[1]}")
                print(f"URL: {record[2]}")
                print(f"Street: {record[3]}")
                print(f"City: {record[4]}")
                print("---")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_database()