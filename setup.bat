@echo off
echo --- UALink 200 Prototype Setup ---
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Install Python 3.9+.
    exit /b 1
)

echo Creating virtual environment...
python -m venv venv

echo Activating venv...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete!
echo Run 'venv\Scripts\activate' to activate.
echo Run 'pytest' to verify tests.
echo Run 'python -m ualink.simulation.testbench' for simulation.
pause
