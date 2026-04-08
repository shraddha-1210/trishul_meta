@echo off
echo ============================================================
echo TRISHUL - FIX ALL ISSUES
echo ============================================================
echo This will fix all common setup issues
echo.
pause

REM Step 1: Activate or create venv
echo.
echo [Step 1/6] Setting up virtual environment...
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Step 2: Install/Reinstall all Python packages
echo [Step 2/6] Installing Python dependencies...
python -m pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
echo.

REM Step 3: Check/Start Neo4j
echo [Step 3/6] Setting up Neo4j...
docker ps | findstr trishul-neo4j >nul 2>&1
if errorlevel 1 (
    echo Neo4j not running. Checking if container exists...
    docker ps -a | findstr trishul-neo4j >nul 2>&1
    if errorlevel 1 (
        echo Creating new Neo4j container...
        docker run -d --name trishul-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/trishul123 neo4j:latest
    ) else (
        echo Starting existing Neo4j container...
        docker start trishul-neo4j
    )
    echo Waiting 20 seconds for Neo4j to initialize...
    timeout /t 20 /nobreak
) else (
    echo Neo4j is already running
)
echo.

REM Step 4: Test Neo4j connection
echo [Step 4/6] Testing Neo4j connection...
venv\Scripts\python.exe test_connection.py
if errorlevel 1 (
    echo WARNING: Neo4j connection test failed
    echo Make sure Neo4j is running and credentials are correct
    echo Default: neo4j/trishul123
    pause
)
echo.

REM Step 5: Seed database
echo [Step 5/6] Seeding database...
venv\Scripts\python.exe backend\graph_seeder.py
echo.

REM Step 6: Create checkpoints
echo [Step 6/6] Creating agent checkpoints...
if not exist checkpoints mkdir checkpoints
venv\Scripts\python.exe create_dummy_checkpoints.py
echo.

echo ============================================================
echo ALL FIXES APPLIED!
echo ============================================================
echo.
echo System is ready. To start:
echo   1. Run this terminal: uvicorn backend.main:app --port 8001 --reload
echo   2. Open new terminal: cd frontend ^&^& npm run dev
echo   3. Open browser: http://localhost:3003
echo.
echo Starting backend now...
pause
venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
