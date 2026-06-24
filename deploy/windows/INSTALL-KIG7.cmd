@echo off
REM ===========================================================================
REM  KIG7 - One-click installer for Windows 10 / 11
REM  Just DOUBLE-CLICK this file. It will ask for Administrator permission
REM  (click "Yes"), then install everything and start both systems.
REM  You do NOT need to know anything about coding.
REM ===========================================================================
setlocal
cd /d "%~dp0"

REM --- Re-launch this file as Administrator if it is not already elevated ---
net session >nul 2>&1
if %errorlevel% NEQ 0 (
    echo.
    echo  Asking Windows for Administrator permission...
    echo  Please click "Yes" on the blue Windows pop-up.
    echo.
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

REM --- We are Administrator now. Run the installer. ---
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Deploy-Kig7.ps1" %*
set "RC=%errorlevel%"

echo.
echo ===========================================================================
if "%RC%"=="0" (
    echo   FINISHED. Both systems should now be open in your web browser:
    echo       Staging:  http://localhost:8073
    echo       Live:     http://localhost:8074
) else if "%RC%"=="3010" (
    echo   The computer needs to RESTART to finish installing Docker.
    echo   After it restarts and you log back in, this installer will
    echo   CONTINUE BY ITSELF. Please just wait for it to finish.
) else (
    echo   Something stopped the installer. Please take a photo of this
    echo   window and send it to your provider. A full log was saved next
    echo   to this file ^(a file starting with "Deploy-Kig7-"^).
)
echo ===========================================================================
echo.
pause
endlocal
