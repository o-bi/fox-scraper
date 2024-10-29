# clean_db.py
import psycopg2

def clean_database():
    try:
        # Database configuration
        db_config = {
            'host': '192.168.1.164',
            'database': 'fox_db',
            'user': 'postgres',
            'password': 'Milena84',
            'port': '5432'
        }
        
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Get current count
        cur.execute("SELECT COUNT(*) FROM collect_ortliche_vet")
        count_before = cur.fetchone()[0]
        print(f"\nCurrent records: {count_before}")
        
        # Clean the table
        cur.execute("TRUNCATE TABLE collect_ortliche_vet RESTART IDENTITY;")
        conn.commit()
        
        # Verify it's clean
        cur.execute("SELECT COUNT(*) FROM collect_ortliche_vet")
        count_after = cur.fetchone()[0]
        print(f"Records after cleanup: {count_after}")
        print(f"Deleted {count_before - count_after} records.")
        
        cur.close()
        conn.close()
        print("\nDatabase cleaned successfully!")
        
    except Exception as e:
        print(f"Error cleaning database: {str(e)}")

if __name__ == "__main__":
    clean_database()