"""
Simple database connection test for Assignment 5
PROG8850 - Database Automation
"""

import mysql.connector
import sys

def test_connection():
    """Test MySQL database connection"""
    try:
        print("🔍 Testing MySQL connection...")
        
        # Connection parameters
        connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Secret5555',
            port=3306
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        print(f"✅ Successfully connected to MySQL!")
        print(f"   MySQL Version: {version[0]}")
        
        # Test if our database exists
        cursor.execute("SHOW DATABASES LIKE 'ecommerce_db'")
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"✅ Database 'ecommerce_db' exists")
            
            # Test tables
            cursor.execute("USE ecommerce_db")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} tables in ecommerce_db:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"   - {table[0]}: {count} rows")
            else:
                print("⚠️  No tables found in ecommerce_db")
        else:
            print("⚠️  Database 'ecommerce_db' does not exist")
        
        cursor.close()
        connection.close()
        print("🔌 Connection closed")
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ MySQL connection failed: {err}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🏪 Assignment 5 - Database Connection Test")
    print("=" * 50)
    
    if test_connection():
        print("\n✅ Database connection test passed!")
        sys.exit(0)
    else:
        print("\n❌ Database connection test failed!")
        print("\nTroubleshooting:")
        print("1. Make sure MySQL is running: ansible-playbook up.yml")
        print("2. Check connection parameters:")
        print("   - Host: 127.0.0.1")
        print("   - User: root") 
        print("   - Password: Secret5555")
        print("   - Port: 3306")
        sys.exit(1)
