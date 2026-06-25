<#
    KIG7 - Windows backup runner (database dump + filestore) for BOTH stacks.

    The repo also ships a Linux/systemd backup runner (deploy/backup-manage.sh +
    deploy/systemd/*), but that one is VPS-only: it targets the *default* compose
    project, needs `flock`, writes to /var/backups, and is fired by a systemd
    timer - none of which exist on this Windows + Docker Desktop machine, which
    runs TWO named stacks (kig7-staging, kig7-live). This script is the Windows
    equivalent: same artifacts and layout, but it backs up each stack and is
    scheduled via a Windows Scheduled Task (see -Register).

    Each run produces, per stack:
        <BackupRoot>\<stack>\<UTCtimestamp>-<trigger>\
            db.dump        (pg_dump -Fc of 18c_hr_project_test)
            filestore.tgz  (tar -czf of /var/lib/odoo/filestore/<db>)
            manifest.json

    Usage (from deploy\windows):
        .\Backup-Kig7.ps1                      # back up both stacks now (trigger=manual)
        .\Backup-Kig7.ps1 -Trigger daily       # back up + prune old sets
        .\Backup-Kig7.ps1 -Stacks staging      # one stack only
        .\Backup-Kig7.ps1 -Register            # install the daily Scheduled Task
        .\Backup-Kig7.ps1 -Unregister          # remove the Scheduled Task
#>
[CmdletBinding()]
param(
    [ValidateSet('manual', 'daily', 'deploy', 'cleanup-only')]
    [string]$Trigger = 'manual',
    [string[]]$Stacks = @('staging', 'live'),
    [string]$BackupRoot = '',
    # Keep ~one month of backups; older sets are pruned on each scheduled run
    # (the newest set is always kept regardless of age).
    [int]$RetentionDays = 30,
    [int]$MinFreeMB = 2048,
    [switch]$Register,
    [switch]$Unregister
)

$ErrorActionPreference = 'Stop'

# --- Resolve our own location (robust against odd launchers) -----------------
$ScriptPath = $PSCommandPath
if (-not $ScriptPath) { $ScriptPath = $MyInvocation.MyCommand.Path }
$ScriptDir  = Split-Path -Parent $ScriptPath
if (-not $BackupRoot) { $BackupRoot = Join-Path $ScriptDir 'backups' }

$RepoRoot  = (Split-Path (Split-Path $ScriptDir -Parent) -Parent)
$OdooConf  = Join-Path $RepoRoot 'configs\docker.odoo.conf'
$LogDir    = Join-Path $BackupRoot 'logs'
$LogFile   = Join-Path $LogDir 'backup.log'
$TaskName  = 'Kig7Backup'

# Stack -> compose project / env-file mapping (matches Deploy-Kig7.ps1).
$StackInfo = @{
    staging = @{ Project = 'kig7-staging'; EnvFile = (Join-Path $ScriptDir 'staging.env') }
    live    = @{ Project = 'kig7-live';    EnvFile = (Join-Path $ScriptDir 'live.env') }
}

function Write-BkLog {
    param([string]$Message)
    $line = "[{0:yyyy-MM-ddTHH:mm:ssZ}] {1}" -f (Get-Date).ToUniversalTime(), $Message
    Write-Host $line
    try { Add-Content -Path $LogFile -Value $line } catch { }
}

# Read db_name from the Odoo config (same source as backup-lib.sh).
function Get-DbName {
    if (-not (Test-Path $OdooConf)) { throw "Missing Odoo config: $OdooConf" }
    foreach ($l in Get-Content $OdooConf) {
        if ($l -match '^\s*db_name\s*=\s*(\S+)') { return $Matches[1] }
    }
    throw "Could not read db_name from $OdooConf"
}

# Resolve the actual container name for a compose service (robust vs the -1 suffix).
function Get-ComposeContainer {
    param([string]$Project, [string]$Service)
    $ErrorActionPreference = 'Continue'
    $name = (& docker ps --filter "label=com.docker.compose.project=$Project" `
                          --filter "label=com.docker.compose.service=$Service" `
                          --filter 'status=running' --format '{{.Names}}' | Select-Object -First 1)
    if ($name) { return $name.Trim() } else { return $null }
}

# Run a native command (all streams -> $null or captured); judge by exit code.
function Invoke-Native {
    param([Parameter(Mandatory)][string]$Exe, [Parameter(Mandatory)][string[]]$Arguments)
    $ErrorActionPreference = 'Continue'   # native stderr must not abort us (PS 5.1)
    & $Exe @Arguments *>> $LogFile
    return $LASTEXITCODE
}

function Wait-DockerReady {
    $ErrorActionPreference = 'Continue'
    for ($i = 0; $i -lt 60; $i++) {
        & docker info *> $null
        if ($LASTEXITCODE -eq 0) { return $true }
        Start-Sleep -Seconds 5
    }
    return $false
}

function Wait-Postgres {
    param([string]$DbContainer)
    $ErrorActionPreference = 'Continue'
    for ($i = 0; $i -lt 30; $i++) {
        & docker exec $DbContainer pg_isready -U odoo -d postgres *> $null
        if ($LASTEXITCODE -eq 0) { return $true }
        Start-Sleep -Seconds 2
    }
    return $false
}

function Backup-Stack {
    param([string]$Stack, [string]$DbName)

    $info = $StackInfo[$Stack]
    if (-not $info) { Write-BkLog "ERROR: unknown stack '$Stack'"; return $false }

    $dbC  = Get-ComposeContainer -Project $info.Project -Service 'db'
    $webC = Get-ComposeContainer -Project $info.Project -Service 'web'
    if (-not $dbC)  { Write-BkLog "ERROR [$Stack]: db container not running (project $($info.Project))";  return $false }
    if (-not $webC) { Write-BkLog "WARN  [$Stack]: web container not running; filestore will be skipped" }

    if (-not (Wait-Postgres -DbContainer $dbC)) {
        Write-BkLog "ERROR [$Stack]: Postgres not ready in $dbC"; return $false
    }

    $ts     = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $setDir = Join-Path (Join-Path $BackupRoot $Stack) "$ts-$Trigger"
    New-Item -ItemType Directory -Force -Path $setDir | Out-Null
    $dumpOut = Join-Path $setDir 'db.dump'
    $fsOut   = Join-Path $setDir 'filestore.tgz'

    # ---- database dump (in-container -Fc, then docker cp = binary-safe) -------
    Write-BkLog "[$Stack] pg_dump -> db.dump"
    $tmpDump = "/tmp/kig7_backup_$ts.dump"
    if ((Invoke-Native 'docker' @('exec', $dbC, 'pg_dump', '-U', 'odoo', '-Fc', '-f', $tmpDump, $DbName)) -ne 0) {
        Write-BkLog "ERROR [$Stack]: pg_dump failed (see backup.log)"
        Remove-Item -Recurse -Force $setDir -ErrorAction SilentlyContinue
        return $false
    }
    Invoke-Native 'docker' @('cp', "${dbC}:$tmpDump", $dumpOut) | Out-Null
    Invoke-Native 'docker' @('exec', $dbC, 'rm', '-f', $tmpDump) | Out-Null

    if (-not (Test-Path $dumpOut) -or (Get-Item $dumpOut).Length -le 0) {
        Write-BkLog "ERROR [$Stack]: db.dump is empty"
        Remove-Item -Recurse -Force $setDir -ErrorAction SilentlyContinue
        return $false
    }

    # ---- filestore archive ----------------------------------------------------
    $fsBytes = 0
    if ($webC) {
        $ErrorActionPreference = 'Continue'
        & docker exec $webC sh -c "test -d /var/lib/odoo/filestore/$DbName" *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-BkLog "[$Stack] tar filestore -> filestore.tgz"
            $tmpFs = "/tmp/kig7_filestore_$ts.tgz"
            if ((Invoke-Native 'docker' @('exec', $webC, 'tar', '-czf', $tmpFs, '-C', '/var/lib/odoo/filestore', $DbName)) -eq 0) {
                Invoke-Native 'docker' @('cp', "${webC}:$tmpFs", $fsOut) | Out-Null
                Invoke-Native 'docker' @('exec', $webC, 'rm', '-f', $tmpFs) | Out-Null
                if (Test-Path $fsOut) { $fsBytes = (Get-Item $fsOut).Length }
            } else {
                Write-BkLog "WARN  [$Stack]: filestore archive failed"
            }
        } else {
            Write-BkLog "WARN  [$Stack]: filestore path /var/lib/odoo/filestore/$DbName missing"
        }
    }

    $dumpBytes = (Get-Item $dumpOut).Length

    # ---- manifest -------------------------------------------------------------
    $manifest = [ordered]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
        trigger       = $Trigger
        stack         = $Stack
        project       = $info.Project
        database      = $DbName
        files         = [ordered]@{ db_dump = 'db.dump'; filestore = 'filestore.tgz' }
        sizes_bytes   = [ordered]@{ db_dump = $dumpBytes; filestore = $fsBytes }
    }
    ($manifest | ConvertTo-Json -Depth 5) | Set-Content -Path (Join-Path $setDir 'manifest.json') -Encoding UTF8

    $fsNote = if ($fsBytes -gt 0) { "{0:N1} MB" -f ($fsBytes / 1MB) } else { 'MISSING' }
    Write-BkLog ("OK    [{0}]: set={1}  db.dump={2:N1} MB  filestore={3}" -f `
        $Stack, (Split-Path -Leaf $setDir), ($dumpBytes / 1MB), $fsNote)
    return $true
}

function Invoke-Retention {
    param([string]$Stack)
    $stackDir = Join-Path $BackupRoot $Stack
    if (-not (Test-Path $stackDir)) { return }
    $sets = Get-ChildItem -Path $stackDir -Directory | Sort-Object LastWriteTimeUtc -Descending
    if ($sets.Count -le 1) { return }
    $cutoff = (Get-Date).AddDays(-$RetentionDays)
    $newest = $sets[0]
    foreach ($s in $sets) {
        if ($s.FullName -eq $newest.FullName) { continue }
        if ($s.LastWriteTime -lt $cutoff) {
            Write-BkLog "[$Stack] retention: removing $($s.Name)"
            Remove-Item -Recurse -Force $s.FullName -ErrorAction SilentlyContinue
        }
    }
}

function Register-BackupTask {
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" -Trigger daily"
    # TWO backups per day (05:00 and 17:00). Each run also prunes sets older than
    # $RetentionDays (~1 month), so old/unneeded backups are deleted automatically.
    $triggers = @(
        (New-ScheduledTaskTrigger -Daily -At '5:00AM'),
        (New-ScheduledTaskTrigger -Daily -At '5:00PM')
    )
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
    # Runs as the logged-in user (Docker Desktop's engine only exists in the user
    # session), at standard privileges - so no admin is needed to back up.
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
        -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $triggers `
        -Settings $settings -Principal $principal -Force | Out-Null
    Write-BkLog "Registered Scheduled Task '$TaskName' (twice daily 05:00 & 17:00, ${RetentionDays}-day retention, runs as $env:USERNAME, catches up missed runs)."
}

# ===========================================================================
#  MAIN
# ===========================================================================
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-BkLog "Unregistered Scheduled Task '$TaskName'."
    exit 0
}
if ($Register) {
    Register-BackupTask
    exit 0
}

# Single-instance guard (replaces flock). Session-local mutex - backups always
# run in the interactive user session, and it needs no special privilege.
$mutex = New-Object System.Threading.Mutex($false, 'Kig7BackupMutex')
if (-not $mutex.WaitOne(0)) {
    Write-BkLog 'ERROR: another backup is already running.'
    exit 2
}

try {
    if (-not (Wait-DockerReady)) {
        Write-BkLog 'ERROR: Docker engine is not ready (is Docker Desktop running?).'
        exit 1
    }

    # Disk space check.
    $freeMB = [math]::Round((Get-PSDrive (Split-Path $BackupRoot -Qualifier).TrimEnd(':')).Free / 1MB)
    if ($freeMB -lt $MinFreeMB) { Write-BkLog "WARN: low disk space (${freeMB}MB free, want >= ${MinFreeMB}MB)" }

    $dbName = Get-DbName
    Write-BkLog "backup start trigger=$Trigger db=$dbName stacks=$($Stacks -join ',')"

    $allOk = $true
    if ($Trigger -ne 'cleanup-only') {
        foreach ($s in $Stacks) {
            if (-not (Backup-Stack -Stack $s -DbName $dbName)) { $allOk = $false }
        }
    }
    if ($Trigger -in @('daily', 'deploy', 'cleanup-only')) {
        foreach ($s in $Stacks) { Invoke-Retention -Stack $s }
    }

    Write-BkLog "backup complete (all_ok=$allOk)"
    if (-not $allOk) { exit 1 }
    exit 0
}
finally {
    $mutex.ReleaseMutex(); $mutex.Dispose()
}
