@echo off
title FoodBridge - Local Food Wastage Management System
color 0A

echo.
echo  =====================================================
echo   FoodBridge - Local Food Wastage Management System
echo  =====================================================
echo.

:: Use the EXACT Python that has plotly, streamlit, sqlalchemy installed
set PYTHON=C:\Users\kumar\AppData\Local\Programs\Python\Python313\python.exe

:: Verify Python path exists
if not exist "%PYTHON%" (
    echo [ERROR] Python not found at: %PYTHON%
    echo Please run: pip install plotly streamlit sqlalchemy pandas
    pause
    exit /b 1
)

echo [1/2] Checking dependencies...
%PYTHON% -m pip install plotly streamlit sqlalchemy pandas --quiet 2>nul
echo  All packages ready!

echo.
echo [2/2] Launching FoodBridge Dashboard...
echo  Open your browser at: http://localhost:8501
echo  Press Ctrl+C to stop the server.
echo.

cd /d "%~dp0"
%PYTHON% -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

pause
