@echo off
echo Starting TRISHUL Frontend...
echo.

REM Check if node_modules exists
if not exist frontend\node_modules (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

echo Frontend starting on http://localhost:3003
echo.
cd frontend
npm run dev
