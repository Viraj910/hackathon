# MongoDB Installation Script for Windows
# This script will download and install MongoDB Community Server

Write-Host "🍃 MongoDB Installation Script for Windows" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "⚠️  This script requires Administrator privileges" -ForegroundColor Yellow
    Write-Host "🔄 Attempting to restart as Administrator..." -ForegroundColor Yellow
    Start-Process PowerShell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Write-Host "✅ Running with Administrator privileges" -ForegroundColor Green

# Function to download files
function Download-File {
    param (
        [string]$Url,
        [string]$OutFile
    )
    
    try {
        Write-Host "📥 Downloading: $OutFile" -ForegroundColor Blue
        Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing
        Write-Host "✅ Downloaded successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Download failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Create temp directory
$tempDir = "$env:TEMP\mongodb_install"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

Write-Host "📁 Using temp directory: $tempDir" -ForegroundColor Blue

# MongoDB download URL (Community Server 7.0)
$mongoUrl = "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-7.0.4-signed.msi"
$mongoInstaller = "$tempDir\mongodb-installer.msi"

# Check if MongoDB is already installed
try {
    $service = Get-Service -Name "MongoDB" -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "✅ MongoDB service already exists" -ForegroundColor Green
        
        if ($service.Status -eq "Running") {
            Write-Host "✅ MongoDB is already running" -ForegroundColor Green
        } else {
            Write-Host "🔄 Starting MongoDB service..." -ForegroundColor Yellow
            Start-Service -Name "MongoDB"
            Write-Host "✅ MongoDB service started" -ForegroundColor Green
        }
        
        Write-Host "🎉 MongoDB is ready to use!" -ForegroundColor Green
        Write-Host "🔗 Connection: mongodb://localhost:27017/" -ForegroundColor Blue
        exit 0
    }
}
catch {
    Write-Host "ℹ️  MongoDB service not found, proceeding with installation..." -ForegroundColor Blue
}

# Download MongoDB installer
Write-Host "🔽 Downloading MongoDB Community Server..." -ForegroundColor Blue
if (-not (Download-File -Url $mongoUrl -OutFile $mongoInstaller)) {
    Write-Host "❌ Failed to download MongoDB installer" -ForegroundColor Red
    exit 1
}

# Install MongoDB
Write-Host "🔧 Installing MongoDB..." -ForegroundColor Blue
try {
    $installArgs = @(
        "/i", 
        $mongoInstaller,
        "/quiet",
        "INSTALLLOCATION=C:\Program Files\MongoDB\Server\7.0\",
        "ADDLOCAL=ServerService,ServerNoService,Client,MongoDBCompass"
    )
    
    Start-Process -FilePath "msiexec.exe" -ArgumentList $installArgs -Wait -NoNewWindow
    Write-Host "✅ MongoDB installation completed" -ForegroundColor Green
}
catch {
    Write-Host "❌ MongoDB installation failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create data directory
$dataDir = "C:\data\db"
if (-not (Test-Path $dataDir)) {
    Write-Host "📁 Creating MongoDB data directory: $dataDir" -ForegroundColor Blue
    New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
    Write-Host "✅ Data directory created" -ForegroundColor Green
}

# Start MongoDB service
Write-Host "🚀 Starting MongoDB service..." -ForegroundColor Blue
try {
    Start-Service -Name "MongoDB" -ErrorAction SilentlyContinue
    Write-Host "✅ MongoDB service started successfully" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Could not start MongoDB service automatically" -ForegroundColor Yellow
    Write-Host "🔧 You may need to start it manually: net start MongoDB" -ForegroundColor Blue
}

# Test MongoDB connection
Write-Host "🔍 Testing MongoDB connection..." -ForegroundColor Blue
Start-Sleep -Seconds 3

try {
    # Test if port 27017 is listening
    $connection = Test-NetConnection -ComputerName "localhost" -Port 27017 -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "✅ MongoDB is accessible on port 27017" -ForegroundColor Green
    } else {
        Write-Host "❌ MongoDB is not accessible on port 27017" -ForegroundColor Red
        Write-Host "🔧 Try restarting the MongoDB service: net stop MongoDB && net start MongoDB" -ForegroundColor Blue
    }
}
catch {
    Write-Host "⚠️  Could not test connection" -ForegroundColor Yellow
}

# Cleanup
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Blue
Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "🎉 MongoDB Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "🔗 Connection String: mongodb://localhost:27017/" -ForegroundColor Blue
Write-Host "📁 Data Directory: C:\data\db" -ForegroundColor Blue
Write-Host "🖥️  MongoDB Compass (GUI): Available in Start Menu" -ForegroundColor Blue
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test connection: python test_mongodb.py" -ForegroundColor White
Write-Host "2. Migrate data: python migrate_to_mongodb.py" -ForegroundColor White
Write-Host "3. Run your app: python app.py" -ForegroundColor White
Write-Host ""

# Pause to show results
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
