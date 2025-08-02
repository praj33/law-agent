#!/usr/bin/env pwsh
# Law Agent API Starter Script

Write-Host "🏛️  LAW AGENT API SERVER" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Starting Law Agent API..." -ForegroundColor Green
Write-Host ""

try {
    python law_agent_minimal.py
}
catch {
    Write-Host "❌ Error starting Law Agent: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "👋 Law Agent API stopped" -ForegroundColor Yellow
