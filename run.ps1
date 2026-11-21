# PowerShell Launch Script for Local Food Wastage Management System
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Local Food Wastage Management System" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
$PYTHON = "C:\Users\kumar\AppData\Local\Programs\Python\Python313\python.exe"

Write-Host ""
Write-Host "  ======================================================" -ForegroundColor Cyan
Write-Host "   FoodBridge - Local Food Wastage Management System" -ForegroundColor Green
Write-Host "  ======================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed or not in your PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/"
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "[1/3] Checking database..." -ForegroundColor Yellow
& $PYTHON -c "import sqlite3; conn=sqlite3.connect('food_waste.db'); r=conn.cursor().execute('SELECT COUNT(*) FROM food_listings').fetchone()[0]; print('  DB Connected: '+str(r)+' food listings'); conn.close()"

Write-Host "[1/2] Checking and installing dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet
Write-Host ""
Write-Host "[2/3] Verifying packages..." -ForegroundColor Yellow
& $PYTHON -m pip install plotly streamlit sqlalchemy pandas --quiet 2>$null
Write-Host "  All packages OK!" -ForegroundColor Green

Write-Host "[2/2] Launching Streamlit..." -ForegroundColor Green
Write-Host "Opening at http://localhost:8501" -ForegroundColor Cyan
python -m streamlit run app.py
Write-Host ""
Write-Host "[3/3] Starting FoodBridge at http://localhost:8501" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

& $PYTHON -m streamlit run app.py
