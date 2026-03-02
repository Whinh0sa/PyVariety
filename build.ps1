$AppPath = "$PSScriptRoot\main.py"
$IconPath = "" # We rely on a default pyinstaller icon if we don't have an .ico
$DistDir = "$PSScriptRoot\dist"

Write-Host "Building PyVariety into an executable..." -ForegroundColor Cyan

# Check if pyinstaller is installed
if (-not (Get-Command "pyinstaller" -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found. Installing now..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Run PyInstaller
# --noconfirm: overwrite existing
# --onedir: creates a folder distribution instead of a single massive block that unpacks to Temp (better performance)
# --windowed: prevents the black console window from appearing
# --name PyVariety
# --collect-all customtkinter: ensures CTK themes and fonts are packaged
pyinstaller --noconfirm --onedir --windowed --name "PyVariety" --collect-all customtkinter --hidden-import pystray --hidden-import PIL._tkinter_finder $AppPath

Write-Host "Build complete! You can find the executable at: $DistDir\PyVariety\PyVariety.exe" -ForegroundColor Green
