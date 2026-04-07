@echo off
echo ========================================
echo TRISHUL Quick Setup
echo ========================================
echo.

echo This will set up everything you need.
echo.
pause

echo Step 1: Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Step 2: Installing Python dependencies...
pip install -r requirements.txt

echo Step 3: Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo Step 4: Checking Neo4j connection...
python check_system.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo Neo4j Setup Required
    echo ========================================
    echo.
    echo Option 1: Docker (Easiest)
    echo   docker run -d --name trishul-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/trishul123 neo4j:latest
    echo.
    echo Option 2: Neo4j Desktop
    echo   1. Download from https://neo4j.com/download/
    echo   2. Create database with password: trishul123
    echo   3. Start the database
    echo.
    echo After Neo4j is running, run this script again.
    echo.
    pause
    exit /b 1
)

echo Step 5: Seeding database...
python -m backend.graph_seeder

echo Step 6: Creating agent checkpoints...
python create_dummy_checkpoints.py

echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo To start TRISHUL, run: run_all.bat
echo.
pause
