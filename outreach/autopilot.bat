@echo off
REM ============================================================
REM  Verispect email autopilot — find + verify + personalize + send + log
REM  Fill the 5 values below ONCE, then this runs the whole thing.
REM  Schedule it daily:  see schedule command at bottom.
REM ============================================================

REM --- your keys/login (fill these) ---
set HUNTER_API_KEY=PASTE_HUNTER_KEY
set SMTP_HOST=mail.spacemail.com
set SMTP_PORT=587
set SMTP_USER=you@yourdomain.com
set SMTP_PASS=PASTE_SPACEMAIL_PASSWORD
set FROM_EMAIL=you@yourdomain.com

cd /d "%~dp0\.."
python outreach\run.py --enrich --send --cap 40

REM ------------------------------------------------------------
REM  To run this every weekday at 09:30 (hands-off), run ONCE in an
REM  admin terminal:
REM
REM  schtasks /create /tn "Verispect Outreach" /tr "\"%~dp0autopilot.bat\"" /sc weekly /d MON,TUE,WED,THU,FRI /st 09:30
REM
REM  Remove it later:  schtasks /delete /tn "Verispect Outreach" /f
REM ------------------------------------------------------------
