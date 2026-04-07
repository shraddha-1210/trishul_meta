@echo off
echo ========================================
echo TRISHUL - Complete Startup
echo ========================================
echo.

echo Step 1: Checking Neo4j...
timeout /t 2 >nul

echo Step 2: Activating Python environment...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Virtual environment not found!
    echo Run: python -m venv venv
    pause
    exit /b 1
)

echo Step 3: Installing dependencies...
pip install -q -r requirements.txt

echo Step 4: Checking database...
python -c "from neo4j import GraphDatabase; import os; from dotenv import load_dotenv; load_dotenv(); driver = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASS'))); result = driver.session().run('MATCH (n) RETURN count(n) as count').single(); count = result['count']; print(f'Database has {count} nodes'); exit(0 if count > 0 else 1)"
if errorlevel 1 (
    echo Database is empty, seeding...
    python -m backend.graph_seeder
)

echo Step 5: Checking checkpoints...
if not exist "checkpoints\red_final.zip" (
    echo Creating checkpoints...
    python create_dummy_checkpoints.py
)

echo Step 6: Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    call npm install
)
cd ..

echo.
echo ========================================
echo Starting TRISHUL...
echo ========================================
echo.
echo Backend will start on: http://localhost:8001
echo Frontend will start on: http://localhost:3001
echo.
echo Press Ctrl+C to stop all services
echo.

start "TRISHUL Backend" cmd /k "venv\Scripts\activate && python -m uvicorn backend.main:app --reload --port 8001"
timeout /t 3 >nul
start "TRISHUL Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ TRISHUL is starting...
echo.
echo Open your browser to: http://localhost:3001
echo.
pause
