@echo off
echo ============================================================
echo TRISHUL - INSTALL AND RUN
echo ============================================================
echo.

REM Step 1: Create venv if needed
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Step 2: Install packages using venv pip
echo Installing Python packages...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\pip.exe install -r requirements.txt

REM Step 3: Start Neo4j
echo Checking Neo4j...
docker ps | findstr trishul-neo4j >nul 2>&1
if errorlevel 1 (
    docker start trishul-neo4j 2>nul || docker run -d --name trishul-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/trishul123 neo4j:latest
    timeout /t 15 /nobreak
)

REM Step 4: Seed database
echo Seeding database...
venv\Scripts\python.exe backend\graph_seeder.py

REM Step 5: Create checkpoints
if not exist checkpoints\red_final.zip (
    echo Creating checkpoints...
    venv\Scripts\python.exe create_dummy_checkpoints.py
)

echo.
echo ============================================================
echo INSTALLATION COMPLETE - STARTING BACKEND
echo ============================================================
echo.
echo Backend: http://localhost:8001
echo.
echo Open NEW terminal and run: start_frontend.bat
echo Then open browser: http://localhost:3003
echo.
pause

venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
