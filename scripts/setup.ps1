$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\AI_Agents\GeminiDailyAggregator"

Write-Host "[1/4] Creating folders..."
$folders = @(
  "$ProjectRoot\inbox",
  "$ProjectRoot\inbox\manual_paste",
  "$ProjectRoot\inbox\gemini_chat_exports",
  "$ProjectRoot\inbox\raw",
  "$ProjectRoot\reports",
  "$ProjectRoot\data",
  "$ProjectRoot\scripts",
  "$ProjectRoot\prompts"
)

foreach ($f in $folders) {
  New-Item -ItemType Directory -Path $f -Force | Out-Null
}

Write-Host "[2/4] Installing Python libraries..."
python -m pip install --upgrade pip
python -m pip install pandas openpyxl beautifulsoup4 pyyaml

Write-Host "[3/4] Checking Gemini CLI..."
if (-not (Get-Command gemini -ErrorAction SilentlyContinue)) {
  Write-Warning "Gemini CLI が見つかりません。npm install -g @google/gemini-cli を実行してください。"
} else {
  gemini --version
}

Write-Host "[4/4] Checking API key environment variables..."
if ($env:GEMINI_API_KEY) {
  Write-Warning "GEMINI_API_KEY が設定されています。Googleログイン方式を使う場合は削除を推奨します。"
}
if ($env:GOOGLE_API_KEY) {
  Write-Warning "GOOGLE_API_KEY が設定されています。Googleログイン方式を使う場合は削除を推奨します。"
}

Write-Host "Setup completed."
