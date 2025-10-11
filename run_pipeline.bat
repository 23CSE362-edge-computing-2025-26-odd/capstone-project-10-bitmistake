@echo off
echo ================================================================================
echo PREDICTIVE PLACEMENT PIPELINE LAUNCHER
echo ================================================================================
echo.

echo Activating conda environment...
call conda activate tensorflow_gpu_env

if errorlevel 1 (
    echo ERROR: Failed to activate conda environment
    echo Please ensure 'tensorflow_gpu_env' exists
    echo.
    pause
    exit /b 1
)

echo.
echo Environment activated successfully
echo.
echo Choose an option:
echo.
echo 1. Safe Pipeline Runner (Recommended - checks everything first)
echo 2. Quick Demo (5 minutes)
echo 3. Complete Pipeline (10-15 minutes)
echo 4. Validation Tests
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running safe pipeline runner...
    python run_pipeline_safe.py
) else if "%choice%"=="2" (
    echo.
    echo Running quick demo...
    python pipeline_demo.py
) else if "%choice%"=="3" (
    echo.
    echo Running complete pipeline...
    python run_complete_pipeline.py
) else if "%choice%"=="4" (
    echo.
    echo Running validation tests...
    python validate_improvements.py
    echo.
    python validate_predictive_placement.py
) else if "%choice%"=="5" (
    echo.
    echo Exiting...
    exit /b 0
) else (
    echo.
    echo Invalid choice. Please run the script again.
)

echo.
echo ================================================================================
echo DONE
echo ================================================================================
echo.
pause
