@echo off
echo ============================================================
echo TRISHUL SYSTEM DIAGNOSTICS
echo ============================================================
echo.

echo [1] Checking Python...
python --version
if errorlevel 1 (
    echo   ERROR: Python not found!
    goto :end
) else (
    echo   OK
)
echo.

echo [2] Checking Virtual Environment...
if exist venv\Scripts\activate.bat (
    echo   OK: Virtual environment exists
) else (
    echo   ERROR: Virtual environment not found
    echo   Run: python -m venv venv
    goto :end
)
echo.

echo [3] Checking Python Packages...
call venv\Scripts\activate.bat
python -c "import neo4j; print('  OK: neo4j installed')" 2>nul || echo   ERROR: neo4j not installed
python -c "import fastapi; print('  OK: fastapi installed')" 2>nul || echo   ERROR: fastapi not installed
python -c "import stable_baselines3; print('  OK: stable-baselines3 installed')" 2>nul || echo   ERROR: stable-baselines3 not installed
echo.

echo [4] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo   WARNING: Docker not found
) else (
    echo   OK: Docker installed
    docker ps | findstr trishul-neo4j >nul 2>&1
    if errorlevel 1 (
        echo   WARNING: Neo4j container not running
    ) else (
        echo   OK: Neo4j container running
    )
)
echo.

echo [5] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Node.js not found
) else (
    node --version
    echo   OK
)
echo.

echo [6] Checking Frontend Dependencies...
if exist frontend\node_modules (
    echo   OK: node_modules exists
) else (
    echo   WARNING: node_modules not found
    echo   Run: cd frontend ^&^& npm install
)
echo.

echo [7] Checking Checkpoints...
if exist checkpoints\red_final.zip (
    echo   OK: red_final.zip exists
) else (
    echo   WARNING: Checkpoints not found
    echo   Run: python create_dummy_checkpoints.py
)
echo.

echo [8] Checking .env file...
if exist .env (
    echo   OK: .env file exists
    type .env
) else (
    echo   ERROR: .env file not found
)
echo.

:end
echo ============================================================
echo DIAGNOSTICS COMPLETE
echo ============================================================
echo.
pause
