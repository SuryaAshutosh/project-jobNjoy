@echo off
REM Job Scraper Agent Setup Script for Windows

echo Setting up Job Scraper Agent...

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

REM Run tests
echo Running tests...
python -m pytest tests/ -v

REM Show success message
echo Setup completed successfully!
echo.
echo To activate the virtual environment, run:
echo   call venv\Scripts\activate
echo.
echo To run the scraper agent, use:
echo   python main.py --mode single
echo.
echo For scheduled scraping, use:
echo   python main.py --mode schedule

pause