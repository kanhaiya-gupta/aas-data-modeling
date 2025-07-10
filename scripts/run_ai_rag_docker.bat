@echo off
REM AI/RAG System Docker Runner Script (Windows)
REM Supports YAML-based query configuration

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=manifests/independent/docker-compose.ai-rag.yml
set CONTAINER_NAME=ai-rag
set SERVICE_NAME=ai-rag

REM Default values
set RAG_QUERY_NAME=
set RAG_CATEGORY=
set RAG_QUERY=
set RAG_ANALYSIS_TYPE=general
set RAG_COLLECTION=aasx_assets
set RAG_LIMIT=5

REM Function to show usage
:show_usage
echo AI/RAG System Docker Runner
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --build                    Build the Docker image
echo   --start                    Start the AI/RAG system
echo   --stop                     Stop the AI/RAG system
echo   --restart                  Restart the AI/RAG system
echo   --logs                     Show logs
echo   --clean                    Clean up containers and volumes
echo   --status                   Show system status
echo.
echo Query Options:
echo   --query-name NAME          Run a specific predefined query by name
echo   --category CATEGORY        Run all queries in a category
echo   --custom-query QUERY       Run a custom query
echo   --demo                     Run demo queries
echo   --list-queries             List all available queries
echo.
echo Analysis Options (for custom queries):
echo   --analysis-type TYPE       Analysis type (general, quality, risk, optimization)
echo   --collection COLLECTION    Vector collection (aasx_assets, aasx_submodels, etc.)
echo   --limit LIMIT              Maximum number of results
echo.
echo Examples:
echo   %0 --build --start
echo   %0 --query-name quality_issues
echo   %0 --category quality_analysis
echo   %0 --custom-query "What are the quality issues?" --analysis-type quality
echo   %0 --demo
echo   %0 --list-queries
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

REM Function to build the image
:build_image
echo [INFO] Building AI/RAG system Docker image...
docker-compose -f "%COMPOSE_FILE%" build "%SERVICE_NAME%"
if errorlevel 1 (
    echo [ERROR] Failed to build image
    exit /b 1
)
echo [SUCCESS] Image built successfully
goto :eof

REM Function to start the system
:start_system
echo [INFO] Starting AI/RAG system...

REM Set environment variables for query
set RAG_QUERY_NAME=%RAG_QUERY_NAME%
set RAG_CATEGORY=%RAG_CATEGORY%
set RAG_QUERY=%RAG_QUERY%
set RAG_ANALYSIS_TYPE=%RAG_ANALYSIS_TYPE%
set RAG_COLLECTION=%RAG_COLLECTION%
set RAG_LIMIT=%RAG_LIMIT%

docker-compose -f "%COMPOSE_FILE%" up -d "%SERVICE_NAME%"
if errorlevel 1 (
    echo [ERROR] Failed to start system
    exit /b 1
)
echo [SUCCESS] AI/RAG system started

REM Wait a moment and show logs
timeout /t 3 /nobreak >nul
call :show_logs
goto :eof

REM Function to stop the system
:stop_system
echo [INFO] Stopping AI/RAG system...
docker-compose -f "%COMPOSE_FILE%" down
echo [SUCCESS] AI/RAG system stopped
goto :eof

REM Function to restart the system
:restart_system
echo [INFO] Restarting AI/RAG system...
call :stop_system
timeout /t 2 /nobreak >nul
call :start_system
goto :eof

REM Function to show logs
:show_logs
echo [INFO] Showing AI/RAG system logs...
docker-compose -f "%COMPOSE_FILE%" logs -f "%SERVICE_NAME%"
goto :eof

REM Function to clean up
:clean_up
echo [WARNING] Cleaning up AI/RAG system containers and volumes...
docker-compose -f "%COMPOSE_FILE%" down -v
docker system prune -f
echo [SUCCESS] Cleanup completed
goto :eof

REM Function to show status
:show_status
echo [INFO] AI/RAG System Status:
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
)

REM Check Qdrant
docker ps | findstr "qdrant" >nul
if errorlevel 1 (
    echo [WARNING] Qdrant is not running
) else (
    echo [SUCCESS] Qdrant is running
)
goto :eof

REM Function to list queries
:list_queries
echo [INFO] Listing available queries from YAML configuration...
python scripts/run_ai_rag.py --list-queries
goto :eof

REM Main script logic
:main
REM Check if Docker is available
call :check_docker

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse

if "%~1"=="--build" (
    call :build_image
    shift
    goto :parse_args
)

if "%~1"=="--start" (
    call :start_system
    shift
    goto :parse_args
)

if "%~1"=="--stop" (
    call :stop_system
    shift
    goto :parse_args
)

if "%~1"=="--restart" (
    call :restart_system
    shift
    goto :parse_args
)

if "%~1"=="--logs" (
    call :show_logs
    shift
    goto :parse_args
)

if "%~1"=="--clean" (
    call :clean_up
    shift
    goto :parse_args
)

if "%~1"=="--status" (
    call :show_status
    shift
    goto :parse_args
)

if "%~1"=="--query-name" (
    set RAG_QUERY_NAME=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--category" (
    set RAG_CATEGORY=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--custom-query" (
    set RAG_QUERY=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--demo" (
    set RAG_DEMO=true
    shift
    goto :parse_args
)

if "%~1"=="--list-queries" (
    call :list_queries
    exit /b 0
)

if "%~1"=="--analysis-type" (
    set RAG_ANALYSIS_TYPE=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--collection" (
    set RAG_COLLECTION=%~2
    shift
    shift
    goto :parse_args
)

if "%~1"=="--limit" (
    set RAG_LIMIT=%~2
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
goto :eof

REM Run main function
call :main %* 
pause 