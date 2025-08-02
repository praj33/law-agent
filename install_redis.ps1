#!/usr/bin/env powershell
# Redis Installation Script for Windows
# Run this script as Administrator

Write-Host "🔧 Redis Installation for Law Agent" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Method 1: Using Chocolatey (Recommended)
Write-Host "🍫 Checking for Chocolatey..." -ForegroundColor Yellow
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "✅ Chocolatey found! Installing Redis..." -ForegroundColor Green
    choco install redis-64 -y
    
    # Start Redis service
    Write-Host "🚀 Starting Redis service..." -ForegroundColor Yellow
    Start-Service redis
    Set-Service -Name redis -StartupType Automatic
    
    Write-Host "✅ Redis installed and started via Chocolatey!" -ForegroundColor Green
    redis-cli ping
    exit 0
}

# Method 2: Download and install manually
Write-Host "📥 Downloading Redis for Windows..." -ForegroundColor Yellow
$redisUrl = "https://github.com/microsoftarchive/redis/releases/download/win-3.2.100/Redis-x64-3.2.100.msi"
$redisInstaller = "$env:TEMP\Redis-x64-3.2.100.msi"

try {
    Invoke-WebRequest -Uri $redisUrl -OutFile $redisInstaller
    Write-Host "✅ Redis downloaded successfully!" -ForegroundColor Green
    
    # Install Redis
    Write-Host "🔧 Installing Redis..." -ForegroundColor Yellow
    Start-Process msiexec.exe -Wait -ArgumentList "/i $redisInstaller /quiet"
    
    # Add Redis to PATH
    $redisPath = "C:\Program Files\Redis"
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($currentPath -notlike "*$redisPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$redisPath", "Machine")
        Write-Host "✅ Redis added to PATH!" -ForegroundColor Green
    }
    
    # Start Redis service
    Write-Host "🚀 Starting Redis service..." -ForegroundColor Yellow
    & "$redisPath\redis-server.exe" --service-install
    & "$redisPath\redis-server.exe" --service-start
    
    Write-Host "✅ Redis installed and started!" -ForegroundColor Green
    Write-Host "🔍 Testing Redis connection..." -ForegroundColor Yellow
    & "$redisPath\redis-cli.exe" ping
    
} catch {
    Write-Host "❌ Error installing Redis: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Try installing Chocolatey first: https://chocolatey.org/install" -ForegroundColor Yellow
}

Write-Host "🎉 Redis setup complete!" -ForegroundColor Green
Write-Host "📝 Redis will now start automatically with Windows" -ForegroundColor Cyan
