@echo off
REM Smart Negotiator - Quick Start Script for Windows
REM Run this script to start the application

echo 🤖 Smart Negotiator - Starting up...
echo ====================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    REM Try new Docker Compose syntax
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Docker Compose is not available. Please install Docker Desktop.
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found. Please make sure it's in the project root.
    pause
    exit /b 1
)

REM Check if API key is configured
findstr /C:"your-friend-should-get-their-own-key-here" .env >nul
if %errorlevel% equ 0 (
    echo ⚠️  API key not configured!
    echo    Please get a Gemini API key from: https://makersuite.google.com/app/apikey
    echo    Then edit the GEMINI_API_KEY in .env file
    echo.
    set /p choice="Do you want to continue anyway? (y/N): "
    if /i not "!choice!"=="y" if /i not "!choice!"=="yes" (
        echo Aborted. Please configure your API key first.
        pause
        exit /b 1
    )
)

echo 🚀 Starting Docker containers...
echo    This may take 2-3 minutes on first run...
echo.

REM Start the application
docker-compose up --build -d

REM Wait a moment for startup
timeout /t 3 /nobreak >nul

REM Check if containers are running
docker-compose ps | findstr /C:"Up" >nul
if %errorlevel% equ 0 (
    echo.
    echo ✅ Application started successfully!
    echo    🌐 Open your browser to: http://localhost:8501
    echo.
    echo 📝 To stop the app later, run: docker-compose down
    echo 📊 To view logs, run: docker-compose logs app
) else (
    echo.
    echo ❌ Failed to start application. Check the logs:
    echo    docker-compose logs app
    pause
    exit /b 1
)

pause</content>
<parameter name="filePath">/Users/saikumarkaparaju/Downloads/smartnegotiator/run.bat