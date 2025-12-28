@echo off
chcp 65001 >nul
echo ======================================
echo 正在执行单元测试...
echo ======================================
echo.

cd /d "%~dp0"

python -m pytest -v --tb=short

echo.
echo ======================================
echo 单元测试执行完毕！
echo ======================================
echo.

rem 使用 PowerShell 播报语音
powershell.exe -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak('单元测试执行完毕')"

pause
