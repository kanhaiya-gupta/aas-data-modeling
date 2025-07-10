@echo off
REM ETL Pipeline Docker Runner Script (Windows)
REM Enhanced version with comprehensive management options

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=manifests/independent/docker-compose.etl.yml
set SERVICE_NAME=etl-pipeline

REM Default values
set ETL_INPUT_DIR=data/aasx-examples
set ETL_OUTPUT_DIR=output/etl_results
set ETL_CONFIG_FILE=scripts/config_etl.yaml
set ETL_VERBOSE=false

REM Function to show usage
:show_usage
echo ETL Pipeline Docker Runner
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --build                    Build the Docker image
echo   --start                    Start the ETL pipeline
echo   --stop                     Stop the ETL pipeline
echo   --restart                  Restart the ETL pipeline
echo   --logs                     Show logs
echo   --clean                    Clean up containers and volumes
echo   --status                   Show system status
echo   --demo                     Run demo ETL processing
echo.
echo Processing Options:
echo   --input-dir DIR            Specify input directory for AASX files
echo   --output-dir DIR           Specify output directory for results
echo   --config-file FILE         Specify ETL configuration file
echo   --verbose                  Enable verbose logging
echo.
echo Examples:
echo   %0 --build --start
echo   %0 --demo
echo   %0 --input-dir data/aasx-examples --output-dir output/results
echo   %0 --status
echo.
goto :eof

REM Function to check if Docker is running
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)
goto :eof

REM Function to check prerequisites
:check_prerequisites
echo [INFO] Checking prerequisites...

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating basic .env file...
    (
        echo # ETL Pipeline Configuration
        echo ETL_INPUT_DIR=data/aasx-examples
        echo ETL_OUTPUT_DIR=output/etl_results
        echo ETL_CONFIG_FILE=scripts/config_etl.yaml
        echo ETL_VERBOSE=false
    ) > .env
    echo [SUCCESS] Created basic .env file
)

REM Check if input directory exists
if not exist data\aasx-examples (
    echo [WARNING] Input directory data/aasx-examples not found. Creating...
    mkdir data\aasx-examples
    echo [SUCCESS] Created input directory
)

REM Check if AASX files exist
dir data\aasx-examples\*.aasx >nul 2>&1
if errorlevel 1 (
    echo [WARNING] No AASX files found in data/aasx-examples/
    echo [INFO] Please place your .aasx files in the data/aasx-examples/ directory
) else (
    echo [SUCCESS] Found AASX files:
    dir data\aasx-examples\*.aasx
)
goto :eof

REM Function to build the image
:build_image
echo [INFO] Building ETL Pipeline Docker image...
docker-compose -f "%COMPOSE_FILE%" build "%SERVICE_NAME%"
if errorlevel 1 (
    echo [ERROR] Failed to build image
    exit /b 1
)
echo [SUCCESS] Image built successfully
goto :eof

REM Function to start the system
:start_system
echo [INFO] Starting ETL Pipeline...

REM Set environment variables
set ETL_INPUT_DIR=%ETL_INPUT_DIR%
set ETL_OUTPUT_DIR=%ETL_OUTPUT_DIR%
set ETL_CONFIG_FILE=%ETL_CONFIG_FILE%
set ETL_VERBOSE=%ETL_VERBOSE%

docker-compose -f "%COMPOSE_FILE%" up -d "%SERVICE_NAME%"
if errorlevel 1 (
    echo [ERROR] Failed to start system
    exit /b 1
)
echo [SUCCESS] ETL Pipeline started

REM Wait a moment and show logs
timeout /t 5 /nobreak >nul
call :show_logs
goto :eof

REM Function to stop the system
:stop_system
echo [INFO] Stopping ETL Pipeline...
docker-compose -f "%COMPOSE_FILE%" down
echo [SUCCESS] ETL Pipeline stopped
goto :eof

REM Function to restart the system
:restart_system
echo [INFO] Restarting ETL Pipeline...
call :stop_system
timeout /t 2 /nobreak >nul
call :start_system
goto :eof

REM Function to show logs
:show_logs
echo [INFO] Showing ETL Pipeline logs...
docker-compose -f "%COMPOSE_FILE%" logs -f "%SERVICE_NAME%"
goto :eof

REM Function to clean up
:clean_up
echo [WARNING] Cleaning up ETL Pipeline containers and volumes...
docker-compose -f "%COMPOSE_FILE%" down -v
docker system prune -f
echo [SUCCESS] Cleanup completed
goto :eof

REM Function to show status
:show_status
echo [INFO] ETL Pipeline Status:
echo.

REM Check if containers are running
docker-compose -f "%COMPOSE_FILE%" ps | findstr "Up" >nul
if errorlevel 1 (
    echo [WARNING] No containers are running
) else (
    echo [SUCCESS] Containers are running
    docker-compose -f "%COMPOSE_FILE%" ps
)

echo.

REM Check input files
if exist data\aasx-examples (
    for /f %%i in ('dir /b data\aasx-examples\*.aasx 2^>nul ^| find /c /v ""') do set aasx_count=%%i
    echo [INFO] Input files: %aasx_count% AASX files found
    if %aasx_count% gtr 0 (
        dir data\aasx-examples\*.aasx
    )
)

REM Check output directory
if exist output\etl_results (
    for /f %%i in ('dir /b /s output\etl_results\*.json output\etl_results\*.csv 2^>nul ^| find /c /v ""') do set output_count=%%i
    echo [INFO] Output files: %output_count% processed files found
)
goto :eof

REM Function to run demo
:run_demo
echo [INFO] Running ETL Pipeline Demo...

REM Check if demo files exist
dir data\aasx-examples\*.aasx >nul 2>&1
if errorlevel 1 (
    echo [WARNING] No AASX files found for demo
    echo [INFO] Please place some .aasx files in data/aasx-examples/ directory
    exit /b 1
)

REM Start the pipeline
call :start_system

echo [SUCCESS] Demo ETL processing started
echo [INFO] Check logs for processing details
goto :eof

REM Main script logic
:main
REM Check if Docker is available
call :check_docker

REM Initialize variables
set has_action=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse

if "%~1"=="--build" (
    call :build_image
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--start" (
    call :start_system
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--stop" (
    call :stop_system
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--restart" (
    call :restart_system
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--logs" (
    call :show_logs
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--clean" (
    call :clean_up
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--status" (
    call :show_status
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--demo" (
    call :run_demo
    set has_action=true
    shift
    goto :parse_args
)

if "%~1"=="--input-dir" (
    set ETL_INPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--output-dir" (
    set ETL_OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--config-file" (
    set ETL_CONFIG_FILE=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--verbose" (
    set ETL_VERBOSE=true
    shift
    goto :parse_args
)

if "%~1"=="--help" (
    call :show_usage
    exit /b 0
)

if "%~1"=="-h" (
    call :show_usage
    exit /b 0
)

echo [ERROR] Unknown option: %~1
call :show_usage
exit /b 1

:end_parse
REM If no action specified, check prerequisites and show usage
if "%has_action%"=="false" (
    call :check_prerequisites
    call :show_usage
    exit /b 0
)
goto :eof

REM Run main function
call :main %* 