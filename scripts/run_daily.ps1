$ErrorActionPreference = "Stop"

$ProjectRoot = "C:\AI_Agents\GeminiDailyAggregator"
Set-Location $ProjectRoot

python ".\scripts\collect_and_summarize.py"
