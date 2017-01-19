@echo off
cd ../../

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PPYTHON_PATH=<PPYTHON_PATH

rem Define some constants for our UberDOG server:
set MAX_CHANNELS=999999
set STATESERVER=4002
set ASTRON_IP=127.0.0.1:7199
set EVENTLOGGER_IP=127.0.0.1:7197

rem Get the user input:
set /P BASE_CHANNEL="Base channel (DEFAULT: 1000000): " || ^
set BASE_CHANNEL=1000000

set /P IS_LIVE="Live Setting (DEFAULT: 0): " || ^
set IS_LIVE=0

echo ===============================
echo Starting Toontown Project Altis UberDOG server...
echo ppython: %PPYTHON_PATH%
echo Base channel: %BASE_CHANNEL%
echo Max channels: %MAX_CHANNELS%
echo State Server: %STATESERVER%
echo Astron IP: %ASTRON_IP%
echo Event Logger IP: %EVENTLOGGER_IP%
echo Live Mode: %IS_LIVE%
echo ===============================

:main
%PPYTHON_PATH% -m toontown.uberdog.ServiceStart --base-channel %BASE_CHANNEL% ^
               --max-channels %MAX_CHANNELS% --stateserver %STATESERVER% ^
               --astron-ip %ASTRON_IP% --eventlogger-ip %EVENTLOGGER_IP% ^
               --want-live %IS_LIVE%
pause
goto main