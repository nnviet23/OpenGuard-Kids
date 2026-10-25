# Cài agent OpenGuard Kids (Windows, chạy bằng PowerShell quản trị). Chỉ dùng trên máy thử nghiệm đã đồng ý.
param([string]$Server = "http://127.0.0.1:8000/api/v1")
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
python -m venv "$here\.venv"
& "$here\.venv\Scripts\pip.exe" install -r "$here\requirements.txt"
$data = Join-Path $env:ProgramData "OpenGuardKids"
New-Item -ItemType Directory -Force $data | Out-Null
# ACL: chỉ SYSTEM và Administrators ghi được; người dùng thường chỉ đọc (để tray hiển thị trạng thái)
icacls $data /inheritance:r /grant:r "SYSTEM:(OI)(CI)F" "Administrators:(OI)(CI)F" "Users:(OI)(CI)RX" | Out-Null
[Environment]::SetEnvironmentVariable("OPENGUARD_SERVER_URL", $Server, "Machine")
Write-Host "Xong. Tiếp theo:"
Write-Host "  $here\.venv\Scripts\python.exe $here\src\main_service.py enroll --code <MA_8_KY_TU>"
Write-Host "  $here\.venv\Scripts\python.exe $here\src\main_service.py service install   # rồi: service start"
Write-Host "  Biểu tượng khay: $here\.venv\Scripts\python.exe $here\src\main_ui.py"
Write-Host "Mặc định dry-run; muốn thực thi đặt OPENGUARD_ENFORCE_LOCK / ENFORCE_APPS / MANAGE_DNS = 1 (Machine)."
