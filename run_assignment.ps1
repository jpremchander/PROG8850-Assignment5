# Assignment 5 - Database Performance Testing Runner
# PROG8850 - Database Automation
# PowerShell version for Windows

Write-Host "🏪 Brazilian E-commerce Database Performance Analysis" -ForegroundColor Cyan
Write-Host "🎯 Assignment 5 - PROG8850" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Gray

# Function to check if MySQL is running
function Test-MySQLConnection {
    Write-Host "🔍 Checking MySQL connection..." -ForegroundColor Yellow
    try {
        $result = mysql -u root -h 127.0.0.1 -pSecret5555 -e "SELECT 1;" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ MySQL is running and accessible" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ MySQL connection failed" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ MySQL connection failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to install Python dependencies
function Install-PythonDependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Failed to install dependencies: $_" -ForegroundColor Red
        exit 1
    }
}

# Function to set up database
function Set-DatabaseSchema {
    Write-Host "🗄️  Setting up database schema..." -ForegroundColor Yellow
    try {
        mysql -u root -h 127.0.0.1 -pSecret5555 -e "source ecommerce_schema.sql"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Database schema created successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create database schema" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Failed to create database schema: $_" -ForegroundColor Red
        exit 1
    }
}

# Function to load data
function Invoke-DataLoader {
    Write-Host "📥 Preparing sample data..." -ForegroundColor Yellow
    try {
        python data_loader.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Data preparation completed" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to prepare data" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Failed to prepare data: $_" -ForegroundColor Red
        exit 1
    }
}

# Function to run performance tests
function Invoke-PerformanceTests {
    Write-Host "🚀 Running performance tests..." -ForegroundColor Yellow
    try {
        python performance_tester.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Performance tests completed successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Performance tests failed" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Performance tests failed: $_" -ForegroundColor Red
        exit 1
    }
}

# Main execution
function Main {
    Write-Host "Starting Assignment 5 execution..." -ForegroundColor Cyan
    
    # Check prerequisites
    if (-not (Test-MySQLConnection)) {
        Write-Host ""
        Write-Host "Please ensure MySQL is running with the following settings:" -ForegroundColor Yellow
        Write-Host "  Host: 127.0.0.1" -ForegroundColor White
        Write-Host "  User: root" -ForegroundColor White
        Write-Host "  Password: Secret5555" -ForegroundColor White
        Write-Host "  Port: 3306" -ForegroundColor White
        Write-Host ""
        Write-Host "You can start MySQL using: ansible-playbook up.yml" -ForegroundColor Cyan
        exit 1
    }
    
    # Install dependencies
    Install-PythonDependencies
    
    # Set up database
    Set-DatabaseSchema
    
    # Load data
    Invoke-DataLoader
    
    # Run performance tests
    Invoke-PerformanceTests
    
    Write-Host ""
    Write-Host "🎉 Assignment 5 completed successfully!" -ForegroundColor Green
    Write-Host "📋 Check the following files for results:" -ForegroundColor Cyan
    Write-Host "   - Terminal output for performance metrics" -ForegroundColor White
    Write-Host "   - ANALYSIS_REPORT.md for detailed analysis" -ForegroundColor White
    Write-Host "   - data/ directory for sample dataset" -ForegroundColor White
}

# Run main function
Main
