@echo off
title UZEX Spot AI Agent (24/7 Service)
color 0A

echo ==========================================================
echo   UZEX Spot Savdolari AI Agenti - 24/7 Ishga Tushirish
echo ==========================================================
echo.

:loop
echo [%date% %time%] Bot ishga tushirilmoqda...
python bot.py

echo.
echo [OGOHLANTIRISH] Bot to'xtadi yoki xatolik yuz berdi!
echo 5 soniyadan so'ng avtomatik qayta ishga tushadi...
timeout /t 5 /nobreak >nul
echo.
goto loop
