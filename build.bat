@echo off
set PIO_EXE=%USERPROFILE%\.platformio\penv\Scripts\platformio.exe
set ENV_NAME=unknown

IF /I "%1"=="RD" set ENV_NAME=esp32dev_Rotary_Display
IF /I "%1"=="PUBLIC" set ENV_NAME=esp32-s3_4m_mini_lepro_tb1_public
IF /I "%1"=="PRIVATE" set ENV_NAME=esp32-s3_4m_mini_lepro_tb1_private
IF /I "%1"=="S3" set ENV_NAME=esp32-s3_4m_mini
IF /I "%1"=="DOM" set ENV_NAME=esp32_domarem

IF "%ENV_NAME%"=="unknown" (
    echo ==========================================
    echo ERROR: ENV nicht gefunden
    echo ==========================================
    echo RD      esp32dev_Rotary_Display
    echo PUBLIC  esp32-s3_4m_mini_lepro_tb1_public
    echo PRIVATE esp32-s3_4m_mini_lepro_tb1_private
    echo S3      esp32-s3_4m_mini
    echo DOM     esp32_domarem
    echo ==========================================
    exit /b 1
)

echo ==========================================
echo STARTE BUILD PROZESS FUER: %ENV_NAME%
echo ==========================================

:: 1. CLEAN
echo [1/3] Bereinige Build-Ordner (Clean)...
"%PIO_EXE%" run -e %ENV_NAME% --target clean
if %errorlevel% neq 0 goto error

:: 2. BUILD FILESYSTEM (SPIFFS/LittleFS)
echo [2/3] Baue Dateisystem (BuildFS)...
"%PIO_EXE%" run -e %ENV_NAME% --target buildfs
if %errorlevel% neq 0 goto error

:: 3. BUILD FIRMWARE
echo [3/3] Kompiliere Firmware (Build)...
"%PIO_EXE%" run -e %ENV_NAME%
if %errorlevel% neq 0 goto error

echo ==========================================
echo BUILD ERFOLGREICH ABGESCHLOSSEN!
echo ==========================================
:: pause
exit /b 0

:error
echo.
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
echo FEHLER BEIM BUILD PROZESS!
echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
:: pause
exit /b 1