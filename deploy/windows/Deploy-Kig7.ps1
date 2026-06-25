<#
    KIG7 - One-click Windows installer (engine behind INSTALL-KIG7.cmd).

    Installs WSL2 + Docker Desktop on a fresh Windows 10/11 machine and brings
    up TWO docker-compose stacks: staging (restored from a bundled backup) and
    live (fresh, data-driven via `-i hr_uae_init_data`).

    Built for a NON-TECHNICAL operator: self-elevates, survives the reboots that
    WSL2/Docker need (auto-resumes ELEVATED via a Scheduled Task + a stage
    file), is fully idempotent (safe to run again), and logs everything.

    Do not run this directly - double-click INSTALL-KIG7.cmd instead.
#>
[CmdletBinding()]
param(
    [switch]$SkipDockerInstall,
    [int]$StagingPort = 8073,
    [int]$LivePort = 8074,
    [string]$LogDir = ''
)

# --- Resolve our own location ROBUSTLY (do NOT rely on $PSScriptRoot, which can
#     be empty depending on how the script is launched) ----------------------
$ScriptPath = $PSCommandPath
if (-not $ScriptPath) { $ScriptPath = $MyInvocation.MyCommand.Path }
if (-not $ScriptPath) { $ScriptPath = $MyInvocation.MyCommand.Definition }
$ScriptDir = if ($ScriptPath) { Split-Path -Parent $ScriptPath } else { (Get-Location).Path }
if (-not $ScriptDir) { $ScriptDir = (Get-Location).Path }

# --- Self-elevate if not Administrator (wait + propagate the child exit code)--
$principal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)) {
    # Pass the path as a single array element; Start-Process quotes it if needed.
    $child = Start-Process -FilePath 'powershell.exe' -Verb RunAs -PassThru -Wait -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $ScriptPath)
    exit $child.ExitCode
}
Set-Location $ScriptDir
$ErrorActionPreference = 'Stop'

# --- Paths / constants ------------------------------------------------------
if (-not $LogDir) { $LogDir = $ScriptDir }
$RepoRoot         = (Split-Path (Split-Path $ScriptDir -Parent) -Parent)
$ArtifactsDir     = Join-Path $ScriptDir 'artifacts'
$StagingDump      = Join-Path $ArtifactsDir 'kig7_db.dump'
$StagingFilestore = Join-Path $ArtifactsDir 'kig7_filestore.tgz'
$StagingEnv       = Join-Path $ScriptDir 'staging.env'
$LiveEnv          = Join-Path $ScriptDir 'live.env'
$StatePath        = Join-Path $ScriptDir '.kig7-stage'
$TaskName         = 'KIG7Resume'
$DbName           = '18c_hr_project_test'
$ScriptVersion    = 'v3 (file-redirect native output)'
$LogFile          = Join-Path $LogDir ("Deploy-Kig7-{0:yyyyMMdd-HHmmss}.log" -f (Get-Date))
$RawLog           = Join-Path $LogDir ("Deploy-Kig7-{0:yyyyMMdd-HHmmss}.raw.log" -f (Get-Date))

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
try { Start-Transcript -Path $LogFile -Append | Out-Null } catch { }

function Write-Log {
    param([string]$Message, [string]$Color = 'Gray')
    Write-Host ("{0:yyyy-MM-dd HH:mm:ss}  {1}" -f (Get-Date), $Message) -ForegroundColor $Color
}
function Write-Step { param([string]$m) Write-Log "==== $m ====" 'Cyan' }
function Write-Ok   { param([string]$m) Write-Log "OK: $m" 'Green' }
function Write-Warn { param([string]$m) Write-Log "WARNING: $m" 'Yellow' }

function Invoke-Logged {
    # Run a native command; judge success by EXIT CODE only. Native tools
    # (docker, pg_restore, wsl) write progress to stderr; in Windows PowerShell
    # 5.1 piping that via 2>&1 under $ErrorActionPreference='Stop' wrongly
    # aborts. So redirect ALL streams to a file with *>> (same mechanism as the
    # working `docker info *> $null`) and never pipe stderr into the console.
    param([Parameter(Mandatory)][string]$FilePath,
          [Parameter(Mandatory)][string[]]$Arguments,
          [int[]]$AllowExit = @(0))
    Write-Log "> $FilePath $($Arguments -join ' ')"
    & $FilePath @Arguments *>> $RawLog
    $code = $LASTEXITCODE
    Write-Log "  (exit $code - full output in $(Split-Path -Leaf $RawLog))"
    if ($AllowExit -notcontains $code) {
        throw "$FilePath exited with code $code (see $(Split-Path -Leaf $RawLog))"
    }
    return $code
}
function Invoke-Tolerant {
    # Run, log to the raw file, NEVER throw (wsl.exe exit codes vary).
    param([Parameter(Mandatory)][string]$FilePath, [Parameter(Mandatory)][string[]]$Arguments)
    Write-Log "> $FilePath $($Arguments -join ' ')"
    try { & $FilePath @Arguments *>> $RawLog } catch { Write-Log "  (ignored) $($_.Exception.Message)" }
}
function Compose {
    param([Parameter(Mandatory)][string]$ProjectName,
          [Parameter(Mandatory)][string]$EnvFile,
          [Parameter(Mandatory)][string[]]$ComposeArgs)
    Invoke-Logged -FilePath 'docker' -Arguments (
        @('compose', '-p', $ProjectName, '--env-file', $EnvFile) + $ComposeArgs)
}

# --- Reboot / resume (Scheduled Task = elevated, hands-free) -----------------
function Test-PendingReboot {
    $keys = @(
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending',
        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired')
    foreach ($k in $keys) { if (Test-Path $k) { return $true } }
    $sm = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager'
    $v = Get-ItemProperty -Path $sm -Name PendingFileRenameOperations -ErrorAction Ignore
    return [bool]($v -and $v.PendingFileRenameOperations)
}
function Unregister-Resume {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
}
function Set-Resume {
    param([int]$NextStage)
    Set-Content -Path $StatePath -Value $NextStage
    # Re-run elevated, automatically, at the next logon of this user (no UAC).
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $princ = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
        -RunLevel Highest -LogonType Interactive
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
        -Principal $princ -Force | Out-Null
}
function Clear-Resume {
    Remove-Item $StatePath -ErrorAction Ignore
    Unregister-Resume
}
function Invoke-Reboot {
    param([int]$NextStage, [string]$Reason)
    Set-Resume -NextStage $NextStage
    Write-Log ''
    Write-Log '###########################################################' 'Yellow'
    Write-Log "  RESTART NEEDED: $Reason" 'Yellow'
    Write-Log '  The computer will restart in 60 seconds.' 'Yellow'
    Write-Log '  After it restarts, just LOG BACK IN with the same user.' 'Yellow'
    Write-Log '  The installer then CONTINUES BY ITSELF - please wait.' 'Yellow'
    Write-Log '###########################################################' 'Yellow'
    try { Stop-Transcript | Out-Null } catch { }
    & shutdown.exe /r /t 60 /c "KIG7 install continues automatically after restart."
    exit 3010
}

# --- Pre-flight (warn, but only HARD-STOP on disk; virtualization is fixed by
#     the WSL2 install + reboot, so never abort a capable machine on it) ------
function Test-Preflight {
    Write-Step 'Checking this computer'
    $hardFail = $false

    $build = 0
    try { $build = [int](Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').CurrentBuildNumber } catch { }
    if ($build -gt 0 -and $build -lt 19041) {
        Write-Warn "Windows build $build is too old; update to version 2004 / build 19041+."
        $hardFail = $true
    } else { Write-Ok "Windows build $build" }

    try {
        $cpu = Get-CimInstance Win32_Processor -ErrorAction Stop
        $cs  = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
        $virtOk = ($cpu.VirtualizationFirmwareEnabled -contains $true) -or $cs.HypervisorPresent
        if (-not $virtOk) {
            Write-Warn "Could not confirm hardware virtualization. If the install fails, turn on 'Virtualization' / 'VT-x' / 'SVM' in the BIOS/UEFI and run again."
        } else { Write-Ok 'Virtualization enabled' }
        $ramGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
        if ($ramGB -lt 4) { Write-Warn "Only $ramGB GB RAM; Docker needs at least 4 GB (8 GB recommended)." }
        else { Write-Ok "$ramGB GB RAM" }
    } catch { Write-Warn "Could not read CPU/RAM info: $($_.Exception.Message)" }

    $free = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
    if ($free -lt 10) { Write-Warn "Only $free GB free on C: (need ~10 GB)."; $hardFail = $true }
    else { Write-Ok "$free GB free on C:" }

    if ($ScriptDir.StartsWith('\\')) {
        Write-Warn 'Run this from a local folder like C:\KIG7 (not a network path).'
    }
    if ($hardFail) { throw 'This computer is not ready (see WARNINGs above). Fix those, then run INSTALL-KIG7 again.' }
}

# --- WSL2 -------------------------------------------------------------------
function Test-WslReady { wsl.exe --status *> $null; return ($LASTEXITCODE -eq 0) }
function Install-Wsl {
    Write-Step 'Installing Windows Subsystem for Linux (WSL2)'
    Invoke-Tolerant -FilePath 'wsl.exe' -Arguments @('--install', '--no-distribution')
}
function Update-Wsl {
    Invoke-Tolerant -FilePath 'wsl.exe' -Arguments @('--update')
    Invoke-Tolerant -FilePath 'wsl.exe' -Arguments @('--set-default-version', '2')
}

# --- Docker Desktop ---------------------------------------------------------
function Test-DockerInstalled { return [bool](Get-Command docker -ErrorAction SilentlyContinue) }
function Install-Docker {
    Write-Step 'Installing Docker Desktop'
    $done = $false
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        try {
            Invoke-Logged -FilePath 'winget' -Arguments @(
                'install', '--id', 'Docker.DockerDesktop', '-e', '--silent',
                '--accept-package-agreements', '--accept-source-agreements') -AllowExit @(0, 3010) | Out-Null
            $done = $true
        } catch { Write-Warn "winget did not complete ($($_.Exception.Message)); using the direct installer." }
    } else { Write-Warn 'winget not available; using the direct installer.' }
    if (-not $done) {
        $installer = Join-Path $env:TEMP 'DockerDesktopInstaller.exe'
        Write-Log 'Downloading Docker Desktop (about 600 MB)...'
        Invoke-WebRequest -UseBasicParsing -OutFile $installer `
            -Uri 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe'
        $p = Start-Process -FilePath $installer -Wait -PassThru -ArgumentList @(
            'install', '--quiet', '--accept-license', '--backend=wsl-2', '--always-run-service')
        if ($p.ExitCode -notin @(0, 3010)) { throw "Docker installer exited with code $($p.ExitCode)" }
    }
    try { net localgroup docker-users "$env:USERNAME" /add *> $null } catch { }
}
function Start-DockerEngine {
    $exe = 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
    if (Test-Path $exe) { Start-Process -FilePath $exe -ErrorAction SilentlyContinue }
    try { Start-Service com.docker.service -ErrorAction SilentlyContinue } catch { }
}
function Wait-Docker {
    param([int]$TimeoutSeconds = 600)
    Write-Step 'Waiting for the Docker engine (can take a few minutes on first run)'
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        docker info *> $null
        if ($LASTEXITCODE -eq 0) { Write-Ok 'Docker engine is ready'; return }
        Start-Sleep -Seconds 5
    }
    throw "Docker did not become ready within $TimeoutSeconds s. Open 'Docker Desktop' once, wait for 'Engine running', then run INSTALL-KIG7 again."
}

# --- Compose helpers --------------------------------------------------------
function Set-EnvPort {
    param([string]$Path, [int]$Port)
    $c = Get-Content -Path $Path -Raw
    $c = $c -replace 'ODOO_PUBLISH_PORT=\d+', "ODOO_PUBLISH_PORT=$Port"
    Set-Content -Path $Path -Value $c -NoNewline
}
function Test-PortFree {
    param([int]$Port, [string]$Label)
    $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        $ownerPid = ($conn | Select-Object -First 1).OwningProcess
        $name = (Get-Process -Id $ownerPid -ErrorAction SilentlyContinue).ProcessName
        Write-Warn "Port $Port ($Label) is already used by '$name' (PID $ownerPid)."
    }
}
function Wait-Postgres {
    param([string]$ProjectName, [string]$EnvFile)
    for ($i = 0; $i -lt 60; $i++) {
        docker compose -p $ProjectName --env-file $EnvFile exec -T db pg_isready -U odoo -d postgres *> $null
        if ($LASTEXITCODE -eq 0) { return }
        Start-Sleep -Seconds 2
    }
    throw "Database for $ProjectName did not become ready."
}
function Test-DbInitialized {
    # True only if the target DB exists AND Odoo has been installed into it.
    param([string]$ProjectName, [string]$EnvFile)
    $q = "SELECT 1 FROM pg_database WHERE datname='$DbName'"
    $exists = docker compose -p $ProjectName --env-file $EnvFile exec -T db psql -U odoo -d postgres -tAc $q 2>$null
    if (($exists | Out-String).Trim() -ne '1') { return $false }
    $q2 = "SELECT 1 FROM information_schema.tables WHERE table_name='ir_module_module' LIMIT 1"
    $tab = docker compose -p $ProjectName --env-file $EnvFile exec -T db psql -U odoo -d $DbName -tAc $q2 2>$null
    return (($tab | Out-String).Trim() -eq '1')
}
function Restore-Staging {
    Write-Step 'STAGING: starting database'
    Compose 'kig7-staging' $StagingEnv @('up', '-d', 'db')
    Wait-Postgres 'kig7-staging' $StagingEnv
    if (Test-DbInitialized 'kig7-staging' $StagingEnv) {
        Write-Log 'Staging database already restored; starting services.'
    } else {
        Write-Step 'STAGING: restoring the backup'
        Compose 'kig7-staging' $StagingEnv @('cp', $StagingDump, 'db:/tmp/kig7_db.dump')
        Compose 'kig7-staging' $StagingEnv @('exec', '-T', 'db', 'dropdb', '-U', 'odoo', '--if-exists', $DbName)
        Compose 'kig7-staging' $StagingEnv @('exec', '-T', 'db', 'pg_restore', '-U', 'odoo', '-d', 'postgres', '--create', '--no-owner', '--no-acl', '/tmp/kig7_db.dump')
        Compose 'kig7-staging' $StagingEnv @('up', '-d', 'web')
        Start-Sleep -Seconds 5
        Compose 'kig7-staging' $StagingEnv @('cp', $StagingFilestore, 'web:/tmp/kig7_filestore.tgz')
        Compose 'kig7-staging' $StagingEnv @('exec', '-u', 'root', '-T', 'web', 'bash', '-lc', 'mkdir -p /var/lib/odoo/filestore && tar -xzf /tmp/kig7_filestore.tgz -C /var/lib/odoo/filestore && chown -R odoo:odoo /var/lib/odoo')
    }
    Compose 'kig7-staging' $StagingEnv @('up', '-d')
    Write-Ok 'Staging is up'
}
function Init-Live {
    Write-Step 'LIVE: starting database'
    Compose 'kig7-live' $LiveEnv @('up', '-d', 'db')
    Wait-Postgres 'kig7-live' $LiveEnv
    if (Test-DbInitialized 'kig7-live' $LiveEnv) {
        Write-Log 'Live database already initialized; starting services.'
    } else {
        Write-Step 'LIVE: installing the data module (sets up the whole system)'
        # hr_uae_init_data depends on the whole project: one install pulls every
        # module plus the master-data seeds.
        Compose 'kig7-live' $LiveEnv @('run', '--rm', '--no-deps', 'web', 'odoo', '-d', $DbName, '-i', 'hr_uae_init_data', '--stop-after-init', '--no-http', '--workers=0', '--max-cron-threads=0')
    }
    Compose 'kig7-live' $LiveEnv @('up', '-d')
    Write-Ok 'Live is up'
}
function Test-Http {
    param([string]$Name, [int]$Port)
    $url = "http://127.0.0.1:$Port/web/login"
    for ($i = 0; $i -lt 36; $i++) {
        try {
            $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
            if ($r.StatusCode -eq 200) { Write-Ok "$Name reachable at $url"; return }
        } catch { }
        Start-Sleep -Seconds 5
    }
    Write-Warn "$Name not reachable yet at $url. It may still be starting; check again in a minute."
}
function Invoke-Stacks {
    Push-Location $RepoRoot
    try {
        Write-Step 'Preparing the two systems'
        Set-EnvPort -Path $StagingEnv -Port $StagingPort
        Set-EnvPort -Path $LiveEnv -Port $LivePort
        Test-PortFree -Port $StagingPort -Label 'staging'
        Test-PortFree -Port $LivePort -Label 'live'
        Compose 'kig7-staging' $StagingEnv @('config', '--quiet')
        Write-Step 'Building the application image (first time downloads ~2 GB)'
        Compose 'kig7-staging' $StagingEnv @('build', 'web')

        if ((Test-Path $StagingDump) -and (Test-Path $StagingFilestore)) {
            Restore-Staging
            Test-Http -Name 'staging' -Port $StagingPort
            $script:StagingDone = $true
        } else {
            Write-Warn "Backup files not found in '$ArtifactsDir' (kig7_db.dump + kig7_filestore.tgz). SKIPPING staging. Copy the two files there and run INSTALL-KIG7 again."
            $script:StagingDone = $false
        }
        Init-Live
        Test-Http -Name 'live' -Port $LivePort
        $script:LiveDone = $true
    } finally { Pop-Location }
}

# ===========================================================================
#  MAIN  (stage-driven, survives reboots)
# ===========================================================================
$stage = if (Test-Path $StatePath) { [int](Get-Content $StatePath) } else { 0 }
if ($stage -gt 0) { Unregister-Resume }   # the resume task fired; remove it so it can't re-trigger
Write-Log "KIG7 installer $ScriptVersion starting (stage $stage). Log: $LogFile" 'Cyan'

try {
    if ($stage -le 0) {
        Test-Preflight
        if (-not (Test-WslReady)) {
            Install-Wsl
            if ((Test-PendingReboot) -or (-not (Test-WslReady))) {
                Invoke-Reboot -NextStage 1 -Reason 'Windows needs to finish turning on WSL2 / virtualization.'
            }
        } else { Write-Ok 'WSL2 already installed' }
        $stage = 1
    }
    if ($stage -le 1) {
        Update-Wsl
        if (-not $SkipDockerInstall -and -not (Test-DockerInstalled)) {
            Install-Docker
            if (Test-PendingReboot) {
                Invoke-Reboot -NextStage 2 -Reason 'Windows needs to finish installing Docker Desktop.'
            }
        } else { Write-Ok 'Docker already installed' }
        $stage = 2
    }
    if ($stage -le 2) {
        Start-DockerEngine
        Wait-Docker -TimeoutSeconds 600
        Invoke-Stacks
        Clear-Resume
    }

    Write-Log ''
    Write-Log '===========================================================' 'Green'
    Write-Log '  ALL DONE.' 'Green'
    if ($script:StagingDone) { Write-Log "  Staging system:  http://localhost:$StagingPort" 'Green' }
    else { Write-Log '  Staging system:  SKIPPED (backup files were missing)' 'Yellow' }
    Write-Log "  Live system:     http://localhost:$LivePort" 'Green'
    Write-Log '  Both start automatically every time the computer starts.' 'Green'
    Write-Log '===========================================================' 'Green'
    try { Stop-Transcript | Out-Null } catch { }
    exit 0
} catch {
    Write-Log "FAILED: $($_.Exception.Message)" 'Red'
    Write-Log "A full log was saved to: $LogFile" 'Red'
    Write-Log 'Take a photo of this window and send it (with the log file) to your provider.' 'Red'
    try { Stop-Transcript | Out-Null } catch { }
    exit 1
}
