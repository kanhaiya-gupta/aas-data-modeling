@echo off
REM AASX Package Explorer Launcher (Windows Batch)
REM Launches the AASX Package Explorer application.

echo 🚀 AASX Package Explorer Launcher
echo ==================================================

REM Get the project root directory (parent of scripts folder)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "EXPLORER_PATH=%PROJECT_ROOT%\AasxPackageExplorer\AasxPackageExplorer.exe"

echo 📁 Project root: %PROJECT_ROOT%
echo 🔍 Explorer path: %EXPLORER_PATH%

REM Check if explorer exists
if not exist "%EXPLORER_PATH%" (
    echo ❌ Error: AASX Package Explorer not found!
    echo    Expected location: %EXPLORER_PATH%
    echo.
    echo 💡 Please ensure:
    echo    1. The AasxPackageExplorer folder exists in the project root
    echo    2. AasxPackageExplorer.exe is present in the folder
    echo    3. Windows Desktop Runtime 3.1 is installed
    pause
    exit /b 1
)

echo ✅ AASX Package Explorer found!

REM Launch the explorer
echo 🚀 Launching AASX Package Explorer...
start "" "%EXPLORER_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo ✅ AASX Package Explorer launched successfully!
    echo.
    echo 💡 Tips:
    echo    - Use File ^> Open to load AASX files
    echo    - Check the content-for-demo folder for sample files
    echo    - Close this window when done
) else (
    echo ❌ Error launching explorer!
    echo.
    echo 💡 Troubleshooting:
    echo    1. Ensure Windows Desktop Runtime 3.1 is installed
    echo    2. Try running as administrator
    echo    3. Check Windows Defender/antivirus settings
)

pause 