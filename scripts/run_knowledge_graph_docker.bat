@echo off
REM Knowledge Graph Docker Runner Script (Windows)
REM Enhanced version with comprehensive management options

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=docker-compose.knowledge-graph.yml
set SERVICE_NAME=knowledge-graph

REM Default values
set KG_DATA_DIR=data/graph_data
set KG_API_PORT=8004
set ETL_OUTPUT_DIR=
set neo4j_only=false

REM Function to show usage
:show_usage
echo Knowledge Graph Docker Runner
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --build                    Build the Docker image
echo   --start                    Start the Knowledge Graph system
echo   --stop                     Stop the Knowledge Graph system
echo   --restart                  Restart the Knowledge Graph system
echo   --logs                     Show logs
echo   --clean                    Clean up containers and volumes
echo   --status                   Show system status
echo   --demo                     Run demo knowledge graph analysis
echo.
echo Data Options:
echo   --data-dir DIR             Specify data directory for graph data
echo   --etl-output DIR           Load data from ETL output directory
echo   --neo4j-only               Start only Neo4j (no knowledge graph processing)
echo   --api-port PORT            Specify API port (default: 8004)
echo.
echo Examples:
echo   %0 --build --start
echo   %0 --demo
echo   %0 --etl-output output/etl_results
echo   %0 --neo4j-only
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
        echo # Knowledge Graph Configuration
        echo NEO4J_URI=neo4j://localhost:7687
        echo NEO4J_USER=neo4j
        echo NEO4J_PASSWORD=Neo4j123
        echo KG_DATA_DIR=data/graph_data
        echo KG_API_PORT=8004
    ) > .env
    echo [SUCCESS] Created basic .env file
)

REM Create necessary directories
echo [INFO] Creating data directories...
mkdir data\graph_data data\processed output logs 2>nul
echo [SUCCESS] Data directories created
goto :eof

REM Function to build the image
:build_image
echo [INFO] Building Knowledge Graph Docker image...
docker-compose -f "%COMPOSE_FILE%" build "%SERVICE_NAME%"
if errorlevel 1 (
    echo [ERROR] Failed to build image
    exit /b 1
)
echo [SUCCESS] Image built successfully
goto :eof

REM Function to start the system
:start_system
echo [INFO] Starting Knowledge Graph system...

REM Set environment variables
set KG_DATA_DIR=%KG_DATA_DIR%
set KG_API_PORT=%KG_API_PORT%
set ETL_OUTPUT_DIR=%ETL_OUTPUT_DIR%

docker-compose -f "%COMPOSE_FILE%" up -d
if errorlevel 1 (
    echo [ERROR] Failed to start system
    exit /b 1
)
echo [SUCCESS] Knowledge Graph system started

REM Wait a moment and show logs
timeout /t 5 /nobreak >nul
call :show_logs
goto :eof

REM Function to stop the system
:stop_system
echo [INFO] Stopping Knowledge Graph system...
docker-compose -f "%COMPOSE_FILE%" down
echo [SUCCESS] Knowledge Graph system stopped
goto :eof

REM Function to restart the system
:restart_system
echo [INFO] Restarting Knowledge Graph system...
call :stop_system
timeout /t 2 /nobreak >nul
call :start_system
goto :eof

REM Function to show logs
:show_logs
echo [INFO] Showing Knowledge Graph logs...
docker-compose -f "%COMPOSE_FILE%" logs -f
goto :eof

REM Function to clean up
:clean_up
echo [WARNING] Cleaning up Knowledge Graph containers and volumes...
docker-compose -f "%COMPOSE_FILE%" down -v
docker system prune -f
echo [SUCCESS] Cleanup completed
goto :eof

REM Function to show status
:show_status
echo [INFO] Knowledge Graph System Status:
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

REM Check Neo4j
docker ps | findstr "neo4j" >nul
if errorlevel 1 (
    echo [WARNING] Neo4j is not running
) else (
    echo [SUCCESS] Neo4j is running
    echo [INFO] Neo4j Browser: http://localhost:7474
    echo [INFO] Neo4j Bolt: bolt://localhost:7687
)

REM Check Knowledge Graph API
docker ps | findstr "knowledge-graph" >nul
if errorlevel 1 (
    echo [WARNING] Knowledge Graph API is not running
) else (
    echo [SUCCESS] Knowledge Graph API is running
    echo [INFO] API URL: http://localhost:%KG_API_PORT%
)

echo.

REM Check data directories
if exist data\graph_data (
    for /f %%i in ('dir /b /s data\graph_data\*.json data\graph_data\*.csv 2^>nul ^| find /c /v ""') do set data_count=%%i
    echo [INFO] Graph data files: %data_count% files found
)

if exist output\etl_results (
    for /f %%i in ('dir /b /s output\etl_results\*.json output\etl_results\*.csv 2^>nul ^| find /c /v ""') do set etl_count=%%i
    echo [INFO] ETL output files: %etl_count% files found
)
goto :eof

REM Function to run demo
:run_demo
echo [INFO] Running Knowledge Graph Demo...

REM Check if we have any data
if exist output\etl_results (
    dir output\etl_results\* >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Found ETL output data, using it for demo
        set ETL_OUTPUT_DIR=output/etl_results
    )
) else if exist data\graph_data (
    dir data\graph_data\* >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Found graph data, using it for demo
    )
) else (
    echo [WARNING] No data found for demo
    echo [INFO] Please run ETL pipeline first or place data in data/graph_data/
    exit /b 1
)

REM Start the system
call :start_system

echo [SUCCESS] Demo Knowledge Graph analysis started
echo [INFO] Check logs for analysis details
echo [INFO] Access Neo4j Browser at: http://localhost:7474
echo [INFO] Access Knowledge Graph API at: http://localhost:%KG_API_PORT%
goto :eof

REM Function to start Neo4j only
:start_neo4j_only
echo [INFO] Starting Neo4j only...

REM Start only Neo4j service
docker-compose -f "%COMPOSE_FILE%" up -d neo4j
if errorlevel 1 (
    echo [ERROR] Failed to start Neo4j
    exit /b 1
)
echo [SUCCESS] Neo4j started

echo [INFO] Neo4j Browser: http://localhost:7474
echo [INFO] Neo4j Bolt: bolt://localhost:7687
echo [INFO] Username: neo4j
echo [INFO] Password: Neo4j123
goto :eof

REM Main script logic
:main
REM Check if Docker is available
call :check_docker

REM Initialize variables
set has_action=false
set neo4j_only=false

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
    if "%neo4j_only%"=="true" (
        call :start_neo4j_only
    ) else (
        call :start_system
    )
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

if "%~1"=="--data-dir" (
    set KG_DATA_DIR=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--etl-output" (
    set ETL_OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--neo4j-only" (
    set neo4j_only=true
    shift
    goto :parse_args
)

if "%~1"=="--api-port" (
    set KG_API_PORT=%~2
    shift
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