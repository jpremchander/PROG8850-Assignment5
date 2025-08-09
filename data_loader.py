"""
Data Loader for Brazilian E-commerce Dataset
Assignment 5 - PROG8850

This script handles downloading and loading the Brazilian E-commerce dataset
"""

import os
import zipfile
import urllib.request
from typing import Optional
import mysql.connector
import pandas as pd

def download_dataset(url: Optional[str] = None, extract_to: str = 'data') -> bool:
    """
    Download and extract the Brazilian E-commerce dataset
    
    Note: The actual dataset needs to be downloaded manually from Kaggle:
    https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce?resource=download
    
    This function provides the framework for automated download if API access is available.
    """
    print("📁 Setting up data directory...")
    
    # Create data directory if it doesn't exist
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
        print(f"✅ Created directory: {extract_to}")
    
    # Check if data already exists
    csv_files = [
        'olist_customers_dataset.csv',
        'olist_orders_dataset.csv',
        'olist_order_items_dataset.csv',
        'olist_order_payments_dataset.csv',
        'olist_order_reviews_dataset.csv',
        'olist_products_dataset.csv',
        'olist_sellers_dataset.csv',
        'product_category_name_translation.csv',
        'olist_geolocation_dataset.csv'
    ]
    
    existing_files = []
    missing_files = []
    
    for csv_file in csv_files:
        file_path = os.path.join(extract_to, csv_file)
        if os.path.exists(file_path):
            existing_files.append(csv_file)
        else:
            missing_files.append(csv_file)
    
    if existing_files:
        print(f"✅ Found {len(existing_files)} existing CSV files:")
        for file in existing_files:
            print(f"   - {file}")
    
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} CSV files:")
        for file in missing_files:
            print(f"   - {file}")
        
        print("\n📥 To complete the assignment, please:")
        print("1. Go to: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
        print("2. Download the 'archive.zip' file (requires Kaggle account)")
        print(f"3. Extract the ZIP file to the '{extract_to}' directory")
        print("4. Run this script again")
        
        return False
    
    print("✅ All required CSV files are present!")
    return True

def create_sample_data(extract_to: str = 'data') -> bool:
    """
    Create sample data for testing when the full dataset is not available
    """
    print("🔧 Creating sample data for testing...")
    
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    
    # Sample customers
    customers_data = {
        'customer_id': ['c1', 'c2', 'c3', 'c4', 'c5'] * 100,
        'customer_unique_id': ['cu1', 'cu2', 'cu3', 'cu4', 'cu5'] * 100,
        'customer_zip_code_prefix': [12345, 23456, 34567, 45678, 56789] * 100,
        'customer_city': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'] * 100,
        'customer_state': ['SP', 'RJ', 'DF', 'BA', 'CE'] * 100
    }
    
    # Sample products with categories
    categories_data = {
        'product_category_name': ['eletrônicos', 'roupas', 'casa', 'livros', 'esportes'],
        'product_category_name_english': ['electronics', 'clothing', 'home', 'books', 'sports']
    }
    
    products_data = {
        'product_id': [f'p{i}' for i in range(1, 201)],
        'product_category_name': (['eletrônicos'] * 40 + ['roupas'] * 40 + ['casa'] * 40 + 
                                ['livros'] * 40 + ['esportes'] * 40),
        'product_name_lenght': [50, 45, 60, 35, 55] * 40,
        'product_description_lenght': [200, 180, 220, 150, 190] * 40,
        'product_photos_qty': [3, 2, 4, 1, 3] * 40,
        'product_weight_g': [500, 300, 800, 200, 600] * 40,
        'product_length_cm': [20, 15, 25, 10, 22] * 40,
        'product_height_cm': [10, 8, 12, 5, 11] * 40,
        'product_width_cm': [15, 12, 18, 8, 16] * 40
    }
    
    # Sample sellers
    sellers_data = {
        'seller_id': [f's{i}' for i in range(1, 51)],
        'seller_zip_code_prefix': list(range(10000, 10050)),
        'seller_city': ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza'] * 10,
        'seller_state': ['SP', 'RJ', 'DF', 'BA', 'CE'] * 10
    }
    
    # Sample orders
    orders_data = {
        'order_id': [f'o{i}' for i in range(1, 1001)],
        'customer_id': (['c1', 'c2', 'c3', 'c4', 'c5'] * 200),
        'order_status': (['delivered'] * 800 + ['shipped'] * 100 + ['processing'] * 100),
        'order_purchase_timestamp': ['2018-01-01 10:00:00'] * 1000,
        'order_approved_at': ['2018-01-01 11:00:00'] * 1000,
        'order_delivered_carrier_date': ['2018-01-02 09:00:00'] * 1000,
        'order_delivered_customer_date': ['2018-01-05 14:00:00'] * 1000,
        'order_estimated_delivery_date': ['2018-01-10 23:59:59'] * 1000
    }
    
    # Sample order items
    order_items_data = {
        'order_id': [],
        'order_item_id': [],
        'product_id': [],
        'seller_id': [],
        'shipping_limit_date': [],
        'price': [],
        'freight_value': []
    }
    
    # Generate order items
    import random
    for i in range(1, 1001):
        items_count = random.randint(1, 5)
        for j in range(1, items_count + 1):
            order_items_data['order_id'].append(f'o{i}')
            order_items_data['order_item_id'].append(j)
            order_items_data['product_id'].append(f'p{random.randint(1, 200)}')
            order_items_data['seller_id'].append(f's{random.randint(1, 50)}')
            order_items_data['shipping_limit_date'].append('2018-01-03 23:59:59')
            order_items_data['price'].append(round(random.uniform(10, 500), 2))
            order_items_data['freight_value'].append(round(random.uniform(5, 50), 2))
    
    # Sample order payments
    order_payments_data = {
        'order_id': [f'o{i}' for i in range(1, 1001)],
        'payment_sequential': [1] * 1000,
        'payment_type': (['credit_card'] * 600 + ['boleto'] * 300 + ['debit_card'] * 100),
        'payment_installments': ([1] * 500 + [2] * 200 + [3] * 150 + [6] * 100 + [12] * 50),
        'payment_value': [round(random.uniform(20, 1000), 2) for _ in range(1000)]
    }
    
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
    
    order_reviews_data = {
        'review_id': [f'r{i}' for i in range(1, 801)],
        'order_id': [f'o{i}' for i in range(1, 801)],
        'review_score': ([5] * 400 + [4] * 200 + [3] * 100 + [2] * 50 + [1] * 50),
        'review_comment_title': ['Avaliação'] * 800,
        'review_comment_message': [random.choice(review_comments) for _ in range(800)],
        'review_creation_date': ['2018-01-06 10:00:00'] * 800,
        'review_answer_timestamp': ['2018-01-07 09:00:00'] * 800
    }
    
    # Sample geolocation
    geolocation_data = {
        'geolocation_zip_code_prefix': list(range(10000, 10100)),
        'geolocation_lat': [-23.5489] * 100,
        'geolocation_lng': [-46.6388] * 100,
        'geolocation_city': ['São Paulo'] * 100,
        'geolocation_state': ['SP'] * 100
    }
    
    # Create CSV files
    datasets = {
        'olist_customers_dataset.csv': customers_data,
        'product_category_name_translation.csv': categories_data,
        'olist_products_dataset.csv': products_data,
        'olist_sellers_dataset.csv': sellers_data,
        'olist_orders_dataset.csv': orders_data,
        'olist_order_items_dataset.csv': order_items_data,
        'olist_order_payments_dataset.csv': order_payments_data,
        'olist_order_reviews_dataset.csv': order_reviews_data,
        'olist_geolocation_dataset.csv': geolocation_data
    }
    
    for filename, data in datasets.items():
        df = pd.DataFrame(data)
        file_path = os.path.join(extract_to, filename)
        df.to_csv(file_path, index=False)
        print(f"✅ Created: {filename} ({len(df)} rows)")
    
    print("✅ Sample data created successfully!")
    return True

def main():
    """Main function to handle data preparation"""
    print("📊 Brazilian E-commerce Dataset Preparation")
    print("🎯 Assignment 5 - PROG8850")
    print("=" * 50)
    
    # Try to check for existing data first
    if not download_dataset():
        print("\n🔧 Creating sample data for testing purposes...")
        create_sample_data()
        print("\n⚠️  Note: This is sample data. For the full assignment,")
        print("   please download the actual dataset from Kaggle.")

if __name__ == "__main__":
    main()
