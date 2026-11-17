@echo off
chcp 65001 > nul
title Soar Proxy Checker - Made By i2tt
cd /d "%~dp0"
python main.py
pause
