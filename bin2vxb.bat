@echo off
rem Make a .vxb for VXRECVB from a .bin (uses PowerShell, built into Windows 7 and later):
rem   bin2vxb prog.bin ADDR [--exec ADDR] [-o out.vxb]      addresses in hex, e.g.
rem   bin2vxb prog.bin 0 --exec 0
if "%~2"=="" (
  echo usage: bin2vxb FILE.bin ADDR [--exec ADDR] [-o OUT.vxb]   addresses in hex, e.g. 1ED0
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bin2vxb.ps1" %*
