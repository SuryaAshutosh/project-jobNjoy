@echo off
REM Auto-Apply Agent Setup Script for Windows

echo Setting up Auto-Apply Agent...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

REM Create directories
echo Creating directories...
mkdir screenshots
mkdir logs

REM Run health check
echo Running health check...
python health_check.py

REM Show success message
echo Setup completed successfully!
echo.
echo To activate the virtual environment, run:
echo   call venv\Scripts\activate
echo.
echo To run the agent, use:
echo   python main.py --mode single
echo.
echo For continuous operation, use:
echo   python main.py --mode continuous --interval 1800

pause