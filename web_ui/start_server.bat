@echo off
echo Starting Predictive edge Placement Web UI...
echo.

call conda activate tensorflow_gpu_env

if errorlevel 1 (
    echo Error: Could not activate conda environment 'tensorflow_gpu_env'
    echo Please make sure the environment exists.
    pause
    exit /b 1
)

echo Environment activated successfully!
echo Starting Flask server on http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python app.py

pause
