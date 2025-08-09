#!/bin/bash

# Assignment 5 - Database Performance Testing Runner
# PROG8850 - Database Automation

echo "🏪 Brazilian E-commerce Database Performance Analysis"
echo "🎯 Assignment 5 - PROG8850"
echo "=" * 60

# Function to check if MySQL is running
check_mysql() {
    echo "🔍 Checking MySQL connection..."
    mysql -u root -h 127.0.0.1 -pSecret5555 -e "SELECT 1;" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ MySQL is running and accessible"
        return 0
    else
        echo "❌ MySQL connection failed"
        return 1
    fi
}

# Function to install Python dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
}

# Function to set up database
setup_database() {
    echo "🗄️  Setting up database schema..."
    mysql -u root -h 127.0.0.1 -pSecret5555 < ecommerce_schema.sql
    if [ $? -eq 0 ]; then
        echo "✅ Database schema created successfully"
    else
        echo "❌ Failed to create database schema"
        exit 1
    fi
}

# Function to load data
load_data() {
    echo "📥 Preparing sample data..."
    python data_loader.py
    if [ $? -eq 0 ]; then
        echo "✅ Data preparation completed"
    else
        echo "❌ Failed to prepare data"
        exit 1
    fi
}

# Function to run performance tests
run_tests() {
    echo "🚀 Running performance tests..."
    python performance_tester.py
    if [ $? -eq 0 ]; then
        echo "✅ Performance tests completed successfully"
    else
        echo "❌ Performance tests failed"
        exit 1
    fi
}

# Main execution
main() {
    echo "Starting Assignment 5 execution..."
    
    # Check prerequisites
    if ! check_mysql; then
        echo "Please ensure MySQL is running with the following settings:"
        echo "  Host: 127.0.0.1"
        echo "  User: root"
        echo "  Password: Secret5555"
        echo "  Port: 3306"
        echo ""
        echo "You can start MySQL using: ansible-playbook up.yml"
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Set up database
    setup_database
    
    # Load data
    load_data
    
    # Run performance tests
    run_tests
    
    echo ""
    echo "🎉 Assignment 5 completed successfully!"
    echo "📋 Check the following files for results:"
    echo "   - Terminal output for performance metrics"
    echo "   - ANALYSIS_REPORT.md for detailed analysis"
    echo "   - data/ directory for sample dataset"
}

# Run main function
main
