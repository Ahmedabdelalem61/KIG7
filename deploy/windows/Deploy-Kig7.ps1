#Requires -RunAsAdministrator
[CmdletBinding()]
param(
    [switch]$SkipDockerInstall,
    [int]$StagingPort = 8073,
    [int]$LivePort = 8074,
    [string]$LogDir = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'

$RepoRoot = (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
$ArtifactsDir = Join-Path $PSScriptRoot 'artifacts'
$StagingDump = Join-Path $ArtifactsDir 'kig7_db.dump'
$StagingFilestore = Join-Path $ArtifactsDir 'kig7_filestore.tgz'
$StagingEnv = Join-Path $PSScriptRoot 'staging.env'
$LiveEnv = Join-Path $PSScriptRoot 'live.env'
$LogFile = Join-Path $LogDir ("Deploy-Kig7-{0:yyyyMMdd-HHmmss}.log" -f (Get-Date))

function Write-Log {
    param([string]$Message)
    $line = "{0:yyyy-MM-dd HH:mm:ss} {1}" -f (Get-Date), $Message
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

function Invoke-Logged {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$ArgumentList
    )
    Write-Log ("> {0} {1}" -f $FilePath, ($ArgumentList -join ' '))
    & $FilePath @ArgumentList 2>&1 | ForEach-Object { Write-Log $_.ToString() }
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath exited with code $LASTEXITCODE"
    }
}

function Compose {
    param(
        [Parameter(Mandatory=$true)][string]$ProjectName,
        [Parameter(Mandatory=$true)][string]$EnvFile,
        [Parameter(Mandatory=$true)][string[]]$Args
    )
    Invoke-Logged -FilePath 'docker' -ArgumentList (@('compose', '-p', $ProjectName, '--env-file', $EnvFile) + $Args)
}

function Wait-Docker {
    param([int]$TimeoutSeconds = 600)
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Log 'Docker engine is ready.'
            return
        }
        Start-Sleep -Seconds 5
    }
    throw "Docker did not become ready within $TimeoutSeconds seconds."
}

function Test-StackRunning {
    param([string]$ProjectName)
    $ids = docker compose -p $ProjectName ps -q 2>$null
    return -not [string]::IsNullOrWhiteSpace(($ids -join ''))
}

function Wait-Postgres {
    param([string]$ProjectName, [string]$EnvFile)
    for ($i = 0; $i -lt 60; $i++) {
        docker compose -p $ProjectName --env-file $EnvFile exec -T db pg_isready -U odoo -d postgres *> $null
        if ($LASTEXITCODE -eq 0) {
            return
        }
        Start-Sleep -Seconds 2
    }
    throw "Postgres did not become ready for $ProjectName."
}

function Ensure-EnvPort {
    param([string]$Path, [int]$Port)
    $content = Get-Content -Path $Path -Raw
    $content = $content -replace 'ODOO_PUBLISH_PORT=\d+', "ODOO_PUBLISH_PORT=$Port"
    Set-Content -Path $Path -Value $content -NoNewline
}

function Restore-Staging {
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('up', '-d', 'db')
    Wait-Postgres -ProjectName 'kig7-staging' -EnvFile $StagingEnv
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('cp', $StagingDump, 'db:/tmp/kig7_db.dump')
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('exec', '-T', 'db', 'dropdb', '-U', 'odoo', '--if-exists', '18c_hr_project_test')
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('exec', '-T', 'db', 'pg_restore', '-U', 'odoo', '-d', 'postgres', '--create', '--no-owner', '--no-acl', '/tmp/kig7_db.dump')
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('up', '-d', 'web')
    Start-Sleep -Seconds 5
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('cp', $StagingFilestore, 'web:/tmp/kig7_filestore.tgz')
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('exec', '-u', 'root', '-T', 'web', 'bash', '-lc', 'mkdir -p /var/lib/odoo/filestore && tar -xzf /tmp/kig7_filestore.tgz -C /var/lib/odoo/filestore && chown -R odoo:odoo /var/lib/odoo')
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('up', '-d', 'proxy')
}

function Init-Live {
    Compose -ProjectName 'kig7-live' -EnvFile $LiveEnv -Args @('up', '-d', 'db')
    Wait-Postgres -ProjectName 'kig7-live' -EnvFile $LiveEnv
    Compose -ProjectName 'kig7-live' -EnvFile $LiveEnv -Args @('run', '--rm', '--no-deps', 'web', 'odoo', '-d', '18c_hr_project_test', '-i', 'hr_uae_app,hr_uae_init_data', '--stop-after-init', '--no-http', '--workers=0', '--max-cron-threads=0')
    Compose -ProjectName 'kig7-live' -EnvFile $LiveEnv -Args @('up', '-d', 'web', 'proxy')
}

function Test-Http {
    param([string]$Name, [int]$Port)
    $url = "http://127.0.0.1:$Port/web/login"
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 20
        Write-Log "$Name smoke test: HTTP $($response.StatusCode) $url"
    } catch {
        throw "$Name smoke test failed for $url. $($_.Exception.Message)"
    }
}

try {
    New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
    Write-Log "KIG7 Windows deployment started from $RepoRoot"

    Write-Log 'Phase 1/7: admin check'
    $principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw 'Run this script from an elevated PowerShell session.'
    }

    Write-Log 'Phase 2/7: WSL2 prerequisites'
    Invoke-Logged -FilePath 'dism.exe' -ArgumentList @('/online', '/enable-feature', '/featurename:Microsoft-Windows-Subsystem-Linux', '/all', '/norestart')
    Invoke-Logged -FilePath 'dism.exe' -ArgumentList @('/online', '/enable-feature', '/featurename:VirtualMachinePlatform', '/all', '/norestart')
    Invoke-Logged -FilePath 'wsl.exe' -ArgumentList @('--set-default-version', '2')

    Write-Log 'Phase 3/7: Docker Desktop'
    docker info *> $null
    if ($LASTEXITCODE -eq 0) {
        Write-Log 'Docker is already running.'
    } elseif ($SkipDockerInstall) {
        throw 'Docker is not running and -SkipDockerInstall was set.'
    } else {
        $installed = $false
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            try {
                Invoke-Logged -FilePath 'winget' -ArgumentList @('install', '--id', 'Docker.DockerDesktop', '-e', '--accept-source-agreements', '--accept-package-agreements')
                $installed = $true
            } catch {
                Write-Log "winget install failed: $($_.Exception.Message)"
            }
        }
        if (-not $installed) {
            $installer = Join-Path $env:TEMP 'DockerDesktopInstaller.exe'
            Invoke-Logged -FilePath 'powershell' -ArgumentList @('-NoProfile', '-Command', "Invoke-WebRequest -Uri 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe' -OutFile '$installer'")
            Invoke-Logged -FilePath $installer -ArgumentList @('install', '--quiet')
        }
        Start-Process 'Docker Desktop' -ErrorAction SilentlyContinue
    }
    Wait-Docker -TimeoutSeconds 600

    Write-Log 'Phase 4/7: compose validate and build'
    Push-Location $RepoRoot
    Ensure-EnvPort -Path $StagingEnv -Port $StagingPort
    Ensure-EnvPort -Path $LiveEnv -Port $LivePort
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('config', '--quiet')
    Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('build', 'web')

    Write-Log 'Phase 5/7: staging stack'
    if (-not (Test-Path $StagingDump) -or -not (Test-Path $StagingFilestore)) {
        throw "Missing staging artifacts. Required files: $StagingDump and $StagingFilestore"
    }
    if (Test-StackRunning -ProjectName 'kig7-staging') {
        Write-Log 'Staging stack already has running containers; ensuring services are up.'
        Compose -ProjectName 'kig7-staging' -EnvFile $StagingEnv -Args @('up', '-d')
    } else {
        Restore-Staging
    }

    Write-Log 'Phase 6/7: live stack'
    if (Test-StackRunning -ProjectName 'kig7-live') {
        Write-Log 'Live stack already has running containers; ensuring services are up.'
        Compose -ProjectName 'kig7-live' -EnvFile $LiveEnv -Args @('up', '-d')
    } else {
        Init-Live
    }

    Write-Log 'Phase 7/7: smoke test and summary'
    Test-Http -Name 'staging' -Port $StagingPort
    Test-Http -Name 'live' -Port $LivePort
    Write-Log "Done. Staging: http://127.0.0.1:$StagingPort Live: http://127.0.0.1:$LivePort Log: $LogFile"
    Pop-Location
} catch {
    Write-Log "FAILED: $($_.Exception.Message)"
    try { Pop-Location } catch { }
    throw
}
