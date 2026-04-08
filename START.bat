@echo off
echo ============================================================
echo TRISHUL - QUICK START
echo ============================================================
echo.

REM Check if venv exists
if not exist venv\Scripts\python.exe (
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run first: INSTALL_AND_RUN.bat
    echo.
    pause
    exit /b 1
)

REM Start Neo4j if not running
docker ps | findstr trishul-neo4j >nul 2>&1
if errorlevel 1 (
    echo Starting Neo4j...
    docker start trishul-neo4j 2>nul || docker run -d --name trishul-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/trishul123 neo4j:latest
    timeout /t 10 /nobreak
)

echo.
echo Starting backend on http://localhost:8001
echo.
echo IMPORTANT: Open NEW terminal and run: start_frontend.bat
echo Then open browser: http://localhost:3003
echo.

venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
