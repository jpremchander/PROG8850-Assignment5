# Assignment 5 Setup Guide
**PROG8850 - Database Automation**

## Alternative Setup Options

Since you may not have Docker or Ansible running, here are alternative ways to complete Assignment 5:

### Option 1: Local MySQL Installation

If you have MySQL installed locally:

1. **Start MySQL Service:**
   ```powershell
   # Using Windows Services
   net start mysql
   # OR if you have MySQL Workbench, start it from there
   ```

2. **Create database and user:**
   ```sql
   -- Connect to MySQL as root
   CREATE DATABASE IF NOT EXISTS ecommerce_db;
   CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY 'Secret5555';
   GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'root'@'127.0.0.1';
   FLUSH PRIVILEGES;
   ```

### Option 2: Docker Desktop (Recommended)

1. **Start Docker Desktop** from Windows Start Menu
2. **Wait for Docker to fully start** (green status)
3. **Run the MySQL container:**
   ```powershell
   cd "c:\Users\premc\OneDrive\Documentos\DatabaseAutomation\PROG8850-Assignment5"
   docker-compose -f mysql-adminer.yml up -d
   ```

### Option 3: Using In-Memory SQLite (For Testing)

If MySQL setup is problematic, I can modify the scripts to use SQLite for demonstration:

<function_calls>
<invoke name="create_file">
<parameter name="content">"""
SQLite version of the performance tester for cases where MySQL isn't available
Assignment 5 - PROG8850 (Alternative implementation)
"""

import sqlite3
import pandas as pd
import time
import os
from typing import Dict, List
import random

class SQLitePerformanceTester:
    def __init__(self, db_path='ecommerce.db'):
        """Initialize SQLite database connection"""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to SQLite database: {self.db_path}")
        except sqlite3.Error as err:
            print(f"❌ Error connecting to SQLite: {err}")
            
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Database connection closed")
    
    def create_database_schema(self):
        """Create the database schema for SQLite"""
        try:
            schema_sql = '''
            -- Drop tables if they exist
            DROP TABLE IF EXISTS order_reviews;
            DROP TABLE IF EXISTS order_payments;
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS product_category_name_translation;
            DROP TABLE IF EXISTS sellers;
            DROP TABLE IF EXISTS customers;
            
            -- Customers table
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                customer_unique_id TEXT,
                customer_zip_code_prefix INTEGER,
                customer_city TEXT,
                customer_state TEXT
            );
            
            -- Sellers table
            CREATE TABLE sellers (
                seller_id TEXT PRIMARY KEY,
                seller_zip_code_prefix INTEGER,
                seller_city TEXT,
                seller_state TEXT
            );
            
            -- Product category name translation
            CREATE TABLE product_category_name_translation (
                product_category_name TEXT PRIMARY KEY,
                product_category_name_english TEXT
            );
            
            -- Products table
            CREATE TABLE products (
                product_id TEXT PRIMARY KEY,
                product_category_name TEXT,
                product_name_lenght INTEGER,
                product_description_lenght INTEGER,
                product_photos_qty INTEGER,
                product_weight_g INTEGER,
                product_length_cm INTEGER,
                product_height_cm INTEGER,
                product_width_cm INTEGER,
                FOREIGN KEY (product_category_name) REFERENCES product_category_name_translation(product_category_name)
            );
            
            -- Orders table
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                order_status TEXT,
                order_purchase_timestamp TEXT,
                order_approved_at TEXT,
                order_delivered_carrier_date TEXT,
                order_delivered_customer_date TEXT,
                order_estimated_delivery_date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
            
            -- Order items table
            CREATE TABLE order_items (
                order_id TEXT,
                order_item_id INTEGER,
                product_id TEXT,
                seller_id TEXT,
                shipping_limit_date TEXT,
                price REAL,
                freight_value REAL,
                PRIMARY KEY (order_id, order_item_id),
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
            );
            
            -- Order payments table
            CREATE TABLE order_payments (
                order_id TEXT,
                payment_sequential INTEGER,
                payment_type TEXT,
                payment_installments INTEGER,
                payment_value REAL,
                PRIMARY KEY (order_id, payment_sequential),
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );
            
            -- Order reviews table
            CREATE TABLE order_reviews (
                review_id TEXT PRIMARY KEY,
                order_id TEXT,
                review_score INTEGER,
                review_comment_title TEXT,
                review_comment_message TEXT,
                review_creation_date TEXT,
                review_answer_timestamp TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );
            '''
            
            # Execute each statement
            statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
            for statement in statements:
                self.cursor.execute(statement)
            
            self.connection.commit()
            print("✅ SQLite database schema created successfully")
        except Exception as e:
            print(f"❌ Error creating schema: {e}")
    
    def create_sample_data(self):
        """Create sample data for testing"""
        print("🔧 Creating sample data for testing...")
        
        # Sample categories
        categories = [
            ('eletrônicos', 'electronics'),
            ('roupas', 'clothing'),
            ('casa', 'home'),
            ('livros', 'books'),
            ('esportes', 'sports')
        ]
        
        self.cursor.executemany(
            "INSERT INTO product_category_name_translation VALUES (?, ?)",
            categories
        )
        
        # Sample customers
        customers_data = []
        for i in range(1, 501):
            customers_data.append((
                f'c{i}',
                f'cu{i}',
                random.randint(10000, 99999),
                random.choice(['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza']),
                random.choice(['SP', 'RJ', 'DF', 'BA', 'CE'])
            ))
        
        self.cursor.executemany(
            "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
            customers_data
        )
        
        # Sample products
        products_data = []
        category_names = [cat[0] for cat in categories]
        for i in range(1, 201):
            products_data.append((
                f'p{i}',
                random.choice(category_names),
                random.randint(30, 100),
                random.randint(100, 500),
                random.randint(1, 5),
                random.randint(100, 2000),
                random.randint(10, 50),
                random.randint(5, 30),
                random.randint(8, 40)
            ))
        
        self.cursor.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            products_data
        )
        
        # Sample sellers
        sellers_data = []
        for i in range(1, 51):
            sellers_data.append((
                f's{i}',
                random.randint(10000, 99999),
                random.choice(['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza']),
                random.choice(['SP', 'RJ', 'DF', 'BA', 'CE'])
            ))
        
        self.cursor.executemany(
            "INSERT INTO sellers VALUES (?, ?, ?, ?)",
            sellers_data
        )
        
        # Sample orders
        orders_data = []
        customer_ids = [f'c{i}' for i in range(1, 501)]
        for i in range(1, 1001):
            orders_data.append((
                f'o{i}',
                random.choice(customer_ids),
                random.choice(['delivered', 'shipped', 'processing']),
                f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00',
                f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00',
                f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00',
                f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00',
                f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            ))
        
        self.cursor.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            orders_data
        )
        
        # Sample order items
        order_items_data = []
        product_ids = [f'p{i}' for i in range(1, 201)]
        seller_ids = [f's{i}' for i in range(1, 51)]
        
        for i in range(1, 1001):
            items_count = random.randint(1, 5)
            for j in range(1, items_count + 1):
                order_items_data.append((
                    f'o{i}',
                    j,
                    random.choice(product_ids),
                    random.choice(seller_ids),
                    f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} 23:59:59',
                    round(random.uniform(10, 500), 2),
                    round(random.uniform(5, 50), 2)
                ))
        
        self.cursor.executemany(
            "INSERT INTO order_items VALUES (?, ?, ?, ?, ?, ?, ?)",
            order_items_data
        )
        
        # Sample order payments
        order_payments_data = []
        for i in range(1, 1001):
            order_payments_data.append((
                f'o{i}',
                1,
                random.choice(['credit_card', 'boleto', 'debit_card']),
                random.choice([1, 2, 3, 6, 12]),
                round(random.uniform(20, 1000), 2)
            ))
        
        self.cursor.executemany(
            "INSERT INTO order_payments VALUES (?, ?, ?, ?, ?)",
            order_payments_data
        )
        
        # Sample order reviews
        review_comments = [
            'Produto excelente, entrega rápida',
            'Qualidade muito boa, recomendo',
            'Chegou no prazo, produto conforme descrição',
            'Gostei muito da compra',
            'Produto de qualidade, vendedor confiável',
            'Entrega demorou mas produto é bom',
            'Não gostei do produto',
            'Produto veio com defeito',
            'Entrega muito lenta',
            'Produto não confere com a descrição'
        ]
        
        order_reviews_data = []
        for i in range(1, 801):
            order_reviews_data.append((
                f'r{i}',
                f'o{i}',
                random.choice([1, 2, 3, 4, 5]),
                'Avaliação',
                random.choice(review_comments),
                f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00',
                f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            ))
        
        self.cursor.executemany(
            "INSERT INTO order_reviews VALUES (?, ?, ?, ?, ?, ?, ?)",
            order_reviews_data
        )
        
        self.connection.commit()
        print("✅ Sample data created successfully!")
        print(f"   - 500 customers")
        print(f"   - 1000 orders")
        print(f"   - {len(order_items_data)} order items")
        print(f"   - 800 reviews")
    
    def time_query(self, query: str, description: str) -> float:
        """Execute a query and measure execution time"""
        start_time = time.time()
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"⏱️  {description}")
            print(f"   Query: {query[:100]}..." if len(query) > 100 else f"   Query: {query}")
            print(f"   Execution Time: {execution_time:.4f} seconds")
            print(f"   Results Count: {len(results)}")
            print()
            
            return execution_time
        except sqlite3.Error as err:
            print(f"❌ Error executing query: {err}")
            return -1
    
    def explain_query(self, query: str, description: str):
        """Use EXPLAIN to analyze query execution plan"""
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        print(f"📊 EXPLAIN for: {description}")
        print(f"   Query: {query}")
        
        try:
            self.cursor.execute(explain_query)
            results = self.cursor.fetchall()
            
            print(f"   Query Plan:")
            for row in results:
                print(f"   {row}")
            print()
            
        except sqlite3.Error as err:
            print(f"❌ Error executing EXPLAIN: {err}")
    
    def run_scalar_field_tests(self) -> Dict[str, float]:
        """Test queries on scalar fields like amounts, dates, etc."""
        print("🔍 Running Scalar Field Performance Tests (SQLite)")
        print("=" * 50)
        
        scalar_queries = [
            ("SELECT * FROM order_items WHERE price > 100", "Price filter > 100"),
            ("SELECT * FROM order_items WHERE price BETWEEN 50 AND 200", "Price range 50-200"),
            ("SELECT order_id, SUM(price) as total FROM order_items GROUP BY order_id HAVING total > 500", "Order total > 500"),
            ("SELECT * FROM orders WHERE order_purchase_timestamp >= '2018-01-01'", "Orders after 2018-01-01"),
            ("SELECT COUNT(*) FROM order_items WHERE freight_value > 20", "Count freight > 20"),
            ("SELECT AVG(price) FROM order_items WHERE price < 1000", "Average price < 1000"),
        ]
        
        results = {}
        for query, description in scalar_queries:
            # First show the execution plan
            self.explain_query(query, description)
            # Then time the query
            execution_time = self.time_query(query, description)
            results[description] = execution_time
        
        return results
    
    def run_fulltext_search_tests(self) -> Dict[str, float]:
        """Test text searches (SQLite doesn't have MATCH...AGAINST, so using LIKE)"""
        print("🔍 Running Text Search Performance Tests (SQLite)")
        print("=" * 50)
        
        fulltext_queries = [
            ("SELECT * FROM order_reviews WHERE review_comment_message LIKE '%produto%'", "Search for 'produto'"),
            ("SELECT * FROM order_reviews WHERE review_comment_message LIKE '%entrega%'", "Search for 'entrega'"),
            ("SELECT * FROM order_reviews WHERE review_comment_message LIKE '%qualidade%' AND review_comment_message LIKE '%excelente%'", "Search 'qualidade excelente'"),
            ("SELECT * FROM order_reviews WHERE review_comment_message LIKE '%rapido%' AND review_comment_message LIKE '%entrega%'", "Search 'rapido entrega'"),
            ("SELECT review_score, COUNT(*) FROM order_reviews WHERE review_comment_message LIKE '%recomendo%' GROUP BY review_score", "Search 'recomendo' grouped by score"),
        ]
        
        results = {}
        for query, description in fulltext_queries:
            # First show the execution plan
            self.explain_query(query, description)
            # Then time the query
            execution_time = self.time_query(query, description)
            results[description] = execution_time
        
        return results
    
    def create_indexes(self):
        """Create indexes to improve query performance"""
        print("🏗️  Creating Indexes for Performance Optimization (SQLite)")
        print("=" * 50)
        
        index_queries = [
            ("CREATE INDEX idx_order_items_price ON order_items(price)", "Index on order_items.price"),
            ("CREATE INDEX idx_order_items_freight ON order_items(freight_value)", "Index on order_items.freight_value"),
            ("CREATE INDEX idx_orders_purchase_timestamp ON orders(order_purchase_timestamp)", "Index on orders.order_purchase_timestamp"),
            ("CREATE INDEX idx_order_items_order_price ON order_items(order_id, price)", "Composite index on order_id, price"),
            ("CREATE INDEX idx_reviews_score ON order_reviews(review_score)", "Index on order_reviews.review_score"),
            ("CREATE INDEX idx_reviews_message ON order_reviews(review_comment_message)", "Index on review_comment_message"),
        ]
        
        for query, description in index_queries:
            try:
                print(f"📋 Creating: {description}")
                self.cursor.execute(query)
                self.connection.commit()
                print(f"✅ {description} created successfully")
            except sqlite3.Error as err:
                if "already exists" in str(err):
                    print(f"⚠️  {description} already exists")
                else:
                    print(f"❌ Error creating {description}: {err}")
        print()
    
    def run_complete_performance_test(self):
        """Run the complete performance testing suite"""
        print("🚀 Starting Complete Database Performance Test (SQLite Demo)")
        print("=" * 60)
        
        # Create schema and data
        self.create_database_schema()
        self.create_sample_data()
        
        # Test queries before indexing
        print("\n📊 BEFORE INDEXING")
        print("=" * 30)
        scalar_before = self.run_scalar_field_tests()
        fulltext_before = self.run_fulltext_search_tests()
        
        # Create indexes
        self.create_indexes()
        
        # Test queries after indexing
        print("\n📊 AFTER INDEXING")
        print("=" * 30)
        scalar_after = self.run_scalar_field_tests()
        fulltext_after = self.run_fulltext_search_tests()
        
        # Compare results
        print("\n📈 PERFORMANCE COMPARISON")
        print("=" * 40)
        
        print("Scalar Field Queries:")
        for test_name in scalar_before:
            before_time = scalar_before[test_name]
            after_time = scalar_after[test_name]
            if before_time > 0 and after_time > 0:
                improvement = ((before_time - after_time) / before_time) * 100
                print(f"  {test_name}:")
                print(f"    Before: {before_time:.4f}s, After: {after_time:.4f}s")
                print(f"    Improvement: {improvement:+.2f}%")
        
        print("\nText Search Queries:")
        for test_name in fulltext_before:
            before_time = fulltext_before[test_name]
            after_time = fulltext_after[test_name]
            if before_time > 0 and after_time > 0:
                improvement = ((before_time - after_time) / before_time) * 100
                print(f"  {test_name}:")
                print(f"    Before: {before_time:.4f}s, After: {after_time:.4f}s")
                print(f"    Improvement: {improvement:+.2f}%")


def main():
    """Main function to run the performance testing"""
    print("🏪 Brazilian E-commerce Database Performance Analysis (SQLite Demo)")
    print("🎯 Assignment 5 - PROG8850")
    print("⚠️  Note: This is a SQLite demonstration version")
    print("=" * 60)
    
    # Initialize the tester
    tester = SQLitePerformanceTester()
    
    try:
        # Connect to database
        tester.connect()
        
        # Run complete performance tests
        tester.run_complete_performance_test()
        
    finally:
        tester.disconnect()

if __name__ == "__main__":
    main()
