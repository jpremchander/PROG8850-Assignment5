"""
Assignment 5 - Database Performance Testing
PROG8850 - Database Automation

This script loads the Brazilian E-commerce dataset and performs performance tests
on scalar field queries and full-text searches before and after adding indexes.
"""

import mysql.connector
import pandas as pd
import time
import os
from typing import Dict, List, Tuple
import glob

class DatabasePerformanceTester:
    def __init__(self, host='127.0.0.1', user='root', password='Secret5555', database='ecommerce_db'):
        """Initialize database connection"""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            self.cursor = self.connection.cursor()
            print(f"✅ Connected to MySQL database: {self.database}")
        except mysql.connector.Error as err:
            print(f"❌ Error connecting to MySQL: {err}")
            
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Database connection closed")
    
    def create_database_schema(self):
        """Create the database schema from SQL file"""
        try:
            with open('ecommerce_schema.sql', 'r') as file:
                sql_script = file.read()
            
            # Execute each statement separately
            statements = sql_script.split(';')
            for statement in statements:
                if statement.strip():
                    self.cursor.execute(statement)
            
            print("✅ Database schema created successfully")
        except Exception as e:
            print(f"❌ Error creating schema: {e}")
    
    def load_csv_data(self, data_directory='data'):
        """Load CSV data into database tables"""
        csv_mappings = {
            'olist_customers_dataset.csv': 'customers',
            'olist_sellers_dataset.csv': 'sellers',
            'product_category_name_translation.csv': 'product_category_name_translation',
            'olist_products_dataset.csv': 'products',
            'olist_orders_dataset.csv': 'orders',
            'olist_order_items_dataset.csv': 'order_items',
            'olist_order_payments_dataset.csv': 'order_payments',
            'olist_order_reviews_dataset.csv': 'order_reviews',
            'olist_geolocation_dataset.csv': 'geolocation'
        }
        
        for csv_file, table_name in csv_mappings.items():
            csv_path = os.path.join(data_directory, csv_file)
            if os.path.exists(csv_path):
                print(f"📥 Loading {csv_file} into {table_name}...")
                try:
                    df = pd.read_csv(csv_path)
                    # Handle NaN values
                    df = df.where(pd.notnull(df), None)
                    
                    # Insert data in chunks to avoid memory issues
                    chunk_size = 1000
                    total_rows = len(df)
                    
                    for i in range(0, total_rows, chunk_size):
                        chunk = df.iloc[i:i+chunk_size]
                        self._insert_dataframe_chunk(chunk, table_name)
                        print(f"   Inserted {min(i+chunk_size, total_rows)}/{total_rows} rows")
                    
                    print(f"✅ Successfully loaded {total_rows} rows into {table_name}")
                
                except Exception as e:
                    print(f"❌ Error loading {csv_file}: {e}")
            else:
                print(f"⚠️  CSV file not found: {csv_path}")
    
    def _insert_dataframe_chunk(self, df, table_name):
        """Insert a DataFrame chunk into the specified table"""
        if len(df) == 0:
            return
            
        # Create placeholders for the INSERT statement
        placeholders = ', '.join(['%s'] * len(df.columns))
        columns = ', '.join(df.columns)
        
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Convert DataFrame to list of tuples
        data = [tuple(row) for row in df.values]
        
        try:
            self.cursor.executemany(sql, data)
        except mysql.connector.Error as err:
            print(f"❌ Error inserting data into {table_name}: {err}")
    
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
        except mysql.connector.Error as err:
            print(f"❌ Error executing query: {err}")
            return -1
    
    def explain_query(self, query: str, description: str):
        """Use EXPLAIN to analyze query execution plan"""
        explain_query = f"EXPLAIN {query}"
        print(f"📊 EXPLAIN for: {description}")
        print(f"   Query: {query}")
        
        try:
            self.cursor.execute(explain_query)
            results = self.cursor.fetchall()
            
            # Print column headers
            columns = [desc[0] for desc in self.cursor.description]
            print(f"   {' | '.join(columns)}")
            print(f"   {'-' * (len(' | '.join(columns)))}")
            
            # Print results
            for row in results:
                formatted_row = [str(item) if item is not None else 'NULL' for item in row]
                print(f"   {' | '.join(formatted_row)}")
            print()
            
        except mysql.connector.Error as err:
            print(f"❌ Error executing EXPLAIN: {err}")
    
    def run_scalar_field_tests(self) -> Dict[str, float]:
        """Test queries on scalar fields like amounts, dates, etc."""
        print("🔍 Running Scalar Field Performance Tests")
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
        """Test full-text searches using MATCH...AGAINST syntax"""
        print("🔍 Running Full-Text Search Performance Tests")
        print("=" * 50)
        
        fulltext_queries = [
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('produto')", "Search for 'produto'"),
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('entrega')", "Search for 'entrega'"),
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('qualidade excelente' IN BOOLEAN MODE)", "Boolean search 'qualidade excelente'"),
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('rapido +entrega' IN BOOLEAN MODE)", "Boolean search 'rapido +entrega'"),
            ("SELECT review_score, COUNT(*) FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('recomendo') GROUP BY review_score", "Search 'recomendo' grouped by score"),
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
        print("🏗️  Creating Indexes for Performance Optimization")
        print("=" * 50)
        
        index_queries = [
            ("CREATE INDEX idx_order_items_price ON order_items(price)", "Index on order_items.price"),
            ("CREATE INDEX idx_order_items_freight ON order_items(freight_value)", "Index on order_items.freight_value"),
            ("CREATE INDEX idx_orders_purchase_timestamp ON orders(order_purchase_timestamp)", "Index on orders.order_purchase_timestamp"),
            ("CREATE INDEX idx_order_items_order_price ON order_items(order_id, price)", "Composite index on order_id, price"),
            ("CREATE INDEX idx_reviews_score ON order_reviews(review_score)", "Index on order_reviews.review_score"),
        ]
        
        for query, description in index_queries:
            try:
                print(f"📋 Creating: {description}")
                self.cursor.execute(query)
                print(f"✅ {description} created successfully")
            except mysql.connector.Error as err:
                if "Duplicate key name" in str(err):
                    print(f"⚠️  {description} already exists")
                else:
                    print(f"❌ Error creating {description}: {err}")
        print()
    
    def run_complete_performance_test(self):
        """Run the complete performance testing suite"""
        print("🚀 Starting Complete Database Performance Test")
        print("=" * 60)
        
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
        
        print("\nFull-Text Search Queries:")
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
    print("🏪 Brazilian E-commerce Database Performance Analysis")
    print("🎯 Assignment 5 - PROG8850")
    print("=" * 60)
    
    # Initialize the tester
    tester = DatabasePerformanceTester()
    
    try:
        # Connect to database
        tester.connect()
        
        # Create schema (uncomment if needed)
        # tester.create_database_schema()
        
        # Load data (uncomment if CSV files are available)
        # tester.load_csv_data()
        
        # Run complete performance tests
        tester.run_complete_performance_test()
        
    finally:
        tester.disconnect()

if __name__ == "__main__":
    main()
