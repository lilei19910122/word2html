@echo off
chcp 65001 >nul
echo starting word to html converter...

:: check if docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo error: docker is not installed, please install docker first
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo error: docker compose is not installed, please install docker compose first
    pause
    exit /b 1
)

:: create uploads directory if it doesn't exist
if not exist "uploads" (
    mkdir uploads
    echo created uploads directory
)

:: stop existing containers if any
echo stopping existing containers...
docker-compose down

:: build and start services
echo building docker image...
docker-compose build --no-cache

echo starting services...
docker-compose up -d

:: wait for service to start
echo waiting for service to start...
timeout /t 15 /nobreak >nul

:: check service status
echo checking service status...
docker-compose ps

:: test health check endpoint
echo testing service health...
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo success: service started successfully!
    echo service url: http://localhost:5000
    echo api documentation: http://localhost:5000/
    echo health check: http://localhost:5000/health
) else (
    echo failed: service startup failed, please check logs
    echo view logs: docker-compose logs
)

echo.
echo common commands:
echo   view logs: docker-compose logs -f
echo   stop service: docker-compose down
echo   restart service: docker-compose restart
echo   enter container: docker-compose exec word2html bash

pause