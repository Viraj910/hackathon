# MongoDB Installation Script for Windows
# Run this in PowerShell as Administrator

Write-Host "🏥 Hospital Management System - MongoDB Setup" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ This script must be run as Administrator" -ForegroundColor Red
    Write-Host "💡 Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Running as Administrator" -ForegroundColor Green

# Function to download file
function Download-File {
    param($url, $output)
    try {
        Write-Host "📥 Downloading $output..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
        return $true
    } catch {
        Write-Host "❌ Failed to download: $_" -ForegroundColor Red
        return $false
    }
}

# Check if MongoDB is already installed
$mongoService = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
if ($mongoService) {
    Write-Host "✅ MongoDB service already exists" -ForegroundColor Green
    
    if ($mongoService.Status -eq "Running") {
        Write-Host "✅ MongoDB is already running" -ForegroundColor Green
    } else {
        Write-Host "🔄 Starting MongoDB service..." -ForegroundColor Yellow
        Start-Service -Name "MongoDB"
        Write-Host "✅ MongoDB service started" -ForegroundColor Green
    }
} else {
    Write-Host "📦 MongoDB not found. Installing..." -ForegroundColor Yellow
    
    # Create temp directory
    $tempDir = "$env:TEMP\mongodb_install"
    if (!(Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    }
    
    # Download MongoDB Community Server
    $mongoUrl = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.5-signed.msi"
    $mongoInstaller = "$tempDir\mongodb-installer.msi"
    
    if (Download-File $mongoUrl $mongoInstaller) {
        Write-Host "🚀 Installing MongoDB..." -ForegroundColor Yellow
        Write-Host "⏳ This may take a few minutes..." -ForegroundColor Yellow
        
        # Install MongoDB silently
        $installArgs = @(
            "/i", $mongoInstaller,
            "/quiet",
            "INSTALLLOCATION=C:\Program Files\MongoDB\Server\7.0\",
            "ADDLOCAL=ServerService,Client,Compass"
        )
        
        Start-Process -FilePath "msiexec.exe" -ArgumentList $installArgs -Wait
        
        Write-Host "✅ MongoDB installation completed" -ForegroundColor Green
        
        # Start MongoDB service
        Write-Host "🔄 Starting MongoDB service..." -ForegroundColor Yellow
        Start-Service -Name "MongoDB"
        Write-Host "✅ MongoDB service started" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to download MongoDB installer" -ForegroundColor Red
        Write-Host "💡 Please download manually from: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
        exit 1
    }
}

# Test MongoDB connection
Write-Host "🔍 Testing MongoDB connection..." -ForegroundColor Yellow

try {
    # Test if MongoDB is listening on port 27017
    $connection = Test-NetConnection -ComputerName "localhost" -Port 27017 -ErrorAction SilentlyContinue
    
    if ($connection.TcpTestSucceeded) {
        Write-Host "✅ MongoDB is running and accessible on port 27017" -ForegroundColor Green
        
        # Test Python connection
        Write-Host "🐍 Testing Python MongoDB connection..." -ForegroundColor Yellow
        
        Set-Location "c:\Users\viraj\OneDrive\Desktop\t5"
        
        $pythonTest = python -c "
try:
    from database import DatabaseManager
    db = DatabaseManager()
    if db.is_connected():
        print('✅ Python MongoDB connection successful!')
    else:
        print('❌ Python MongoDB connection failed')
except Exception as e:
    print(f'❌ Error: {e}')
" 2>&1
        
        Write-Host $pythonTest -ForegroundColor Cyan
        
    } else {
        Write-Host "❌ MongoDB is not accessible on port 27017" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error testing MongoDB connection: $_" -ForegroundColor Red
}

Write-Host "`n🎉 MongoDB Setup Complete!" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Run: python test_mongodb.py" -ForegroundColor White
Write-Host "   2. Run: python migrate_to_mongodb.py" -ForegroundColor White
Write-Host "   3. Run: python app.py" -ForegroundColor White
Write-Host "   4. Visit: http://localhost:5000" -ForegroundColor White

Write-Host "`n🔧 MongoDB Management Commands:" -ForegroundColor Yellow
Write-Host "   Start:  net start MongoDB" -ForegroundColor White
Write-Host "   Stop:   net stop MongoDB" -ForegroundColor White
Write-Host "   Status: Get-Service MongoDB" -ForegroundColor White

Write-Host "`n📱 MongoDB Compass (GUI) should be installed" -ForegroundColor Yellow
Write-Host "   Connect to: mongodb://localhost:27017" -ForegroundColor White
