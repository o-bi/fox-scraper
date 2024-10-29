# verify_data.py
import psycopg2
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

def verify_database():
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
        
        # Get total count
        cur.execute("SELECT COUNT(*) FROM collect_ortliche_vet;")
        total_count = cur.fetchone()[0]
        print(f"\nTotal records: {total_count}")
        
        # Get count by page number
        cur.execute("""
            SELECT 
                (metadata->>'page_number')::int as page,
                COUNT(*) as count
            FROM collect_ortliche_vet
            WHERE metadata->>'page_number' IS NOT NULL
            GROUP BY page
            ORDER BY page;
        """)
        
        pages = cur.fetchall()
        print("\nRecords per page:")
        for page, count in pages:
            print(f"Page {page}: {count} records")
        
        # Check for duplicates
        cur.execute("""
            SELECT url, COUNT(*)
            FROM collect_ortliche_vet
            GROUP BY url
            HAVING COUNT(*) > 1;
        """)
        
        duplicates = cur.fetchall()
        if duplicates:
            print("\nFound duplicate URLs:")
            for url, count in duplicates:
                print(f"{url}: {count} occurrences")
        else:
            print("\nNo duplicate URLs found")
        
        # Sample of records
        cur.execute("""
            SELECT id, title, 
                   metadata->>'page_number' as page,
                   metadata->'address'->>'city' as city
            FROM collect_ortliche_vet
            ORDER BY id DESC
            LIMIT 5;
        """)
        
        print("\nLatest records:")
        for record in cur.fetchall():
            print(f"ID: {record[0]}, Page: {record[2]}, City: {record[3]}")
            print(f"Title: {record[1]}")
            print("---")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    verify_database()