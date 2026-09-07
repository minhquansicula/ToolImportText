@echo off
echo Building Paper to Excel OCR...

IF NOT EXIST ".venv" (
    echo Creating virtual environment...
    uv venv
)

echo Activating virtual environment and installing dependencies...
call .venv\Scripts\activate
uv pip install -r requirements.txt
uv pip install pyinstaller

echo Running PyInstaller...
pyinstaller paper_to_excel.spec

echo Build complete! Executable is in dist\
pause
