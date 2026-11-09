@echo off
title Systematic Trader Pro PC Server
cd /d "%~dp0"
python -m streamlit run main.py
pause