@echo off
echo 🚀 Starting Core Components: ETL Pipeline + Knowledge Graph

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found!
    echo Please create a .env file with your configuration.
    pause
    exit /b 1
)

REM Build core Docker images
echo 📦 Building core Docker images...
docker-compose -f docker-compose.core.yml build

REM Start core services
echo 🚀 Starting core services...
docker-compose -f docker-compose.core.yml up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service status
echo 📊 Core Service Status:
docker-compose -f docker-compose.core.yml ps

REM Show access URLs
echo.
echo 🌐 Core Component URLs:
echo    ETL Pipeline API:     http://localhost:8003
echo    Knowledge Graph API:  http://localhost:8004
echo    Neo4j Browser:        http://localhost:7474
echo    Neo4j Bolt:           bolt://localhost:7687

echo.
echo 📁 Data Directories:
echo    Input Data:           ./data/
echo    Output Results:       ./output/
echo    Logs:                 ./logs/

echo.
echo ✅ Core components are ready!
echo.
echo 🔧 Management Commands:
echo    View logs:            docker-compose -f docker-compose.core.yml logs -f
echo    Stop services:        docker-compose -f docker-compose.core.yml down
echo    Restart services:     docker-compose -f docker-compose.core.yml restart
echo.
echo 📚 Next Steps:
echo    1. Place AASX files in ./data/aasx-examples/
echo    2. Run ETL pipeline to process data
echo    3. Access knowledge graph for analysis

pause 