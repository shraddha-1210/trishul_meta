@echo off
echo ========================================
echo TRISHUL Setup and Seed Script
echo ========================================
echo.

echo Step 1: Activating virtual environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo Step 2: Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 3: Installing Frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    echo Make sure Node.js is installed
    pause
    exit /b 1
)
cd ..

echo.
echo Step 4: Seeding Neo4j database...
python -m backend.graph_seeder
if errorlevel 1 (
    echo ERROR: Failed to seed database
    echo Make sure Neo4j is running on bolt://localhost:7687
    pause
    exit /b 1
)

echo.
echo Step 5: Creating dummy checkpoints...
python create_dummy_checkpoints.py
if errorlevel 1 (
    echo ERROR: Failed to create checkpoints
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Setup complete.
echo ========================================
echo.
echo Next steps:
echo 1. Open a new terminal and run: start_backend.bat
echo 2. Open another terminal and run: start_frontend.bat
echo 3. Open browser to http://localhost:3000
echo.
pause
