"""
Assignment 5 - Database Performance Testing with Docker MySQL
PROG8850 - Database Automation

This script loads the Brazilian E-commerce dataset and performs performance tests
on scalar field queries and full-text searches before and after adding indexes.
Uses docker exec for MySQL connection when direct connection fails.
"""

import subprocess
import json
import time
import os
from typing import Dict, List, Tuple
import random

class DockerMySQLPerformanceTester:
    def __init__(self, container_name='prog8850-assignment5-db-1', user='root', password='Secret5555', database='ecommerce_db'):
        """Initialize Docker MySQL connection"""
        self.container_name = container_name
        self.user = user
        self.password = password
        self.database = database
        
    def execute_sql(self, query: str, fetch_results: bool = True) -> List[Tuple]:
        """Execute SQL query using docker exec"""
        try:
            # Escape quotes in the query
            escaped_query = query.replace('"', '\\"').replace("'", "\\'")
            
            cmd = [
                'docker', 'exec', '-i', self.container_name,
                'mysql', '-u', self.user, f'-p{self.password}',
                '-D', self.database,
                '-e', query
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if fetch_results and result.stdout:
                # Parse the output - skip the header line and split by tabs
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    results = []
                    for line in lines[1:]:
                        if line.strip():
                            results.append(tuple(line.split('\t')))
                    return results
                return []
            return []
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing query: {e.stderr}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []
    
    def connect(self):
        """Test connection"""
        try:
            result = self.execute_sql("SELECT 1", fetch_results=True)
            if result:
                print(f"✅ Connected to MySQL database via Docker: {self.container_name}")
                return True
            else:
                print(f"❌ Failed to connect to MySQL database")
                return False
        except Exception as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample data for testing"""
        print("🔧 Creating sample data for testing...")
        
        # Clear existing data
        tables = ['order_reviews', 'order_payments', 'order_items', 'orders', 'products', 'sellers', 'customers', 'product_category_name_translation']
        for table in tables:
            self.execute_sql(f"DELETE FROM {table}", fetch_results=False)
        
        # Sample categories
        categories = [
            ('eletrônicos', 'electronics'),
            ('roupas', 'clothing'),
            ('casa', 'home'),
            ('livros', 'books'),
            ('esportes', 'sports')
        ]
        
        for cat_pt, cat_en in categories:
            self.execute_sql(f"INSERT INTO product_category_name_translation VALUES ('{cat_pt}', '{cat_en}')", fetch_results=False)
        
        # Sample customers
        cities = ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza']
        states = ['SP', 'RJ', 'DF', 'BA', 'CE']
        
        for i in range(1, 501):
            city = random.choice(cities)
            state = random.choice(states)
            zip_code = random.randint(10000, 99999)
            self.execute_sql(f"INSERT INTO customers VALUES ('c{i}', 'cu{i}', {zip_code}, '{city}', '{state}')", fetch_results=False)
        
        # Sample products
        category_names = [cat[0] for cat in categories]
        for i in range(1, 201):
            category = random.choice(category_names)
            name_len = random.randint(30, 100)
            desc_len = random.randint(100, 500)
            photos = random.randint(1, 5)
            weight = random.randint(100, 2000)
            length = random.randint(10, 50)
            height = random.randint(5, 30)
            width = random.randint(8, 40)
            self.execute_sql(f"INSERT INTO products VALUES ('p{i}', '{category}', {name_len}, {desc_len}, {photos}, {weight}, {length}, {height}, {width})", fetch_results=False)
        
        # Sample sellers
        for i in range(1, 51):
            city = random.choice(cities)
            state = random.choice(states)
            zip_code = random.randint(10000, 99999)
            self.execute_sql(f"INSERT INTO sellers VALUES ('s{i}', {zip_code}, '{city}', '{state}')", fetch_results=False)
        
        # Sample orders
        statuses = ['delivered', 'shipped', 'processing']
        for i in range(1, 1001):
            customer_id = f'c{random.randint(1, 500)}'
            status = random.choice(statuses)
            purchase_date = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            approved_date = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            delivered_carrier = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            delivered_customer = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            estimated_delivery = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            
            self.execute_sql(f"INSERT INTO orders VALUES ('o{i}', '{customer_id}', '{status}', '{purchase_date}', '{approved_date}', '{delivered_carrier}', '{delivered_customer}', '{estimated_delivery}')", fetch_results=False)
        
        # Sample order items
        item_count = 0
        for i in range(1, 1001):
            items_in_order = random.randint(1, 5)
            for j in range(1, items_in_order + 1):
                product_id = f'p{random.randint(1, 200)}'
                seller_id = f's{random.randint(1, 50)}'
                shipping_date = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} 23:59:59'
                price = round(random.uniform(10, 500), 2)
                freight = round(random.uniform(5, 50), 2)
                
                self.execute_sql(f"INSERT INTO order_items VALUES ('o{i}', {j}, '{product_id}', '{seller_id}', '{shipping_date}', {price}, {freight})", fetch_results=False)
                item_count += 1
        
        # Sample order payments
        payment_types = ['credit_card', 'boleto', 'debit_card']
        installments_options = [1, 2, 3, 6, 12]
        for i in range(1, 1001):
            payment_type = random.choice(payment_types)
            installments = random.choice(installments_options)
            value = round(random.uniform(20, 1000), 2)
            self.execute_sql(f"INSERT INTO order_payments VALUES ('o{i}', 1, '{payment_type}', {installments}, {value})", fetch_results=False)
        
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
        
        for i in range(1, 801):
            score = random.choice([1, 2, 3, 4, 5])
            comment = random.choice(review_comments)
            creation_date = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            answer_date = f'2018-{random.randint(1,12):02d}-{random.randint(1,28):02d} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00'
            
            # Escape single quotes in comment
            comment = comment.replace("'", "\\'")
            self.execute_sql(f"INSERT INTO order_reviews VALUES ('r{i}', 'o{i}', {score}, 'Avaliação', '{comment}', '{creation_date}', '{answer_date}')", fetch_results=False)
        
        print("✅ Sample data created successfully!")
        print(f"   - 500 customers")
        print(f"   - 1000 orders")
        print(f"   - {item_count} order items")
        print(f"   - 800 reviews")
    
    def time_query(self, query: str, description: str) -> float:
        """Execute a query and measure execution time"""
        start_time = time.time()
        try:
            results = self.execute_sql(query, fetch_results=True)
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"⏱️  {description}")
            print(f"   Query: {query[:100]}..." if len(query) > 100 else f"   Query: {query}")
            print(f"   Execution Time: {execution_time:.4f} seconds")
            print(f"   Results Count: {len(results)}")
            print()
            
            return execution_time
        except Exception as err:
            print(f"❌ Error executing query: {err}")
            return -1
    
    def explain_query(self, query: str, description: str):
        """Use EXPLAIN to analyze query execution plan"""
        explain_query = f"EXPLAIN {query}"
        print(f"📊 EXPLAIN for: {description}")
        print(f"   Query: {query}")
        
        try:
            results = self.execute_sql(explain_query, fetch_results=True)
            
            if results:
                # Print headers (assuming standard EXPLAIN output)
                headers = ['id', 'select_type', 'table', 'partitions', 'type', 'possible_keys', 'key', 'key_len', 'ref', 'rows', 'filtered', 'Extra']
                print(f"   {'  |  '.join(headers[:6])}")  # Show first 6 columns
                print(f"   {'-' * 60}")
                
                # Print results
                for row in results:
                    formatted_row = [str(item) if item != 'NULL' and item is not None else 'NULL' for item in row[:6]]
                    print(f"   {'  |  '.join(formatted_row)}")
            print()
            
        except Exception as err:
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
        
        # First, let's create a full-text index on review comments
        print("🔧 Creating FULLTEXT index for review comments...")
        self.execute_sql("ALTER TABLE order_reviews ADD FULLTEXT(review_comment_title, review_comment_message)", fetch_results=False)
        
        fulltext_queries = [
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('produto')", "Search for 'produto'"),
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('entrega')", "Search for 'entrega'"),
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('qualidade excelente' IN BOOLEAN MODE)", "Boolean search 'qualidade excelente'"),
            ("SELECT * FROM order_reviews WHERE MATCH(review_comment_title, review_comment_message) AGAINST('+entrega +rápida' IN BOOLEAN MODE)", "Boolean search '+entrega +rápida'"),
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
                self.execute_sql(query, fetch_results=False)
                print(f"✅ {description} created successfully")
            except Exception as err:
                if "Duplicate key name" in str(err) or "already exists" in str(err):
                    print(f"⚠️  {description} already exists")
                else:
                    print(f"❌ Error creating {description}: {err}")
        print()
    
    def run_complete_performance_test(self):
        """Run the complete performance testing suite"""
        print("🚀 Starting Complete Database Performance Test")
        print("=" * 60)
        
        # Create sample data
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
    print("🎯 Assignment 5 - PROG8850 (Docker MySQL Version)")
    print("=" * 60)
    
    # Initialize the tester
    tester = DockerMySQLPerformanceTester()
    
    # Connect to database
    if not tester.connect():
        print("❌ Failed to connect to MySQL. Make sure Docker container is running.")
        return
    
    # Run complete performance tests
    tester.run_complete_performance_test()
    
    print("\n🎉 Assignment 5 completed successfully!")
    print("📋 Results show the impact of database indexing on query performance.")

if __name__ == "__main__":
    main()
