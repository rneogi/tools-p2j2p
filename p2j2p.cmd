@echo off
setlocal

set "PYTHON_EXE=C:/Users/raja.neogi/AppData/Local/Programs/Python/Python312/python.exe"

if exist "%PYTHON_EXE%" (
  "%PYTHON_EXE%" "tools/p2j2p.py" %*
) else (
  python "tools/p2j2p.py" %*
)

exit /b %errorlevel%
