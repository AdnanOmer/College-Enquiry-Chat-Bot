@echo off
setlocal

echo ==============================
echo  Starting the Chat bot server
echo ==============================

REM ------------------------------
REM Run Python (tfidf_model.py)
REM ------------------------------
set PY_CMD=

if exist venv\Scripts\python.exe (
    echo  Found venv
    set PY_CMD=venv\Scripts\python.exe
) else (
    echo  venv not found, using system Python
    set PY_CMD=python
)

REM Use cmd /k to keep the window open on error
start "TFIDF Model" cmd /k "%PY_CMD% services\tfidf_model.py"

REM ------------------------------
REM Run Node.js (server.js)
REM ------------------------------
if exist server.js (
    echo  Starting server.js
    start "Node Server" cmd /k "node server.js"
) else (
    echo  server.js not found
    goto END
)

REM ------------------------------
REM Open browser after services
REM ------------------------------
echo  Waiting a few seconds for services to start...
timeout /t 5 >nul

echo  Opening browser at http://localhost:3000
start http://localhost:3000

:END
echo ==============================
echo  All services started
echo ==============================

endlocal
pause
