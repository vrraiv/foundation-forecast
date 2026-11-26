# Monthly registry job for Windows Task Scheduler. Run daily; it does nothing unless a run is due.
#
#   1. `ffcast registry-status`: is the current origin (25th or next business day) done?
#      Not due (registry off, no pre-registration, or already done): log one line and stop.
#      If the status command fails or gives no answer, log STATUS FAILED and exit 6.
#   2. `ffcast registry-run`: snapshot, forecast, seal, ledger line, time stamp. A run started
#      after the origin day is recorded as late by the registry itself. If the run fails, the job
#      stops with a non-zero exit code; nothing was sealed, and tomorrow's start tries again.
#      A run interrupted after sealing is completed by the same command.
#   3. `ffcast registry-verify`: every ledger line against the private files.
#   4. Backup, if `scripts/registry_backup.ps1` exists (set up by the owner; restic to OneDrive).
#   5. Commit and push `ledger/ledger.jsonl` only. If the push fails the commit stays local and
#      the next start pushes it; the time stamp already proves the date independently.
#
# Nothing private is committed: `registry/` and `data/` are git-ignored, and step 5 stages one
# file by name. Results go to `registry/job.log` (private). The exit code is 0 only if every
# step that ran succeeded, so "Last Run Result" in Task Scheduler shows a failure.
#
# Register (owner, once, after HUMAN GATE 5), daily at 18:00, catching up after a missed start:
#   $a = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-NoProfile -File C:\projects\foundation-forecast\scripts\registry_job.ps1"
#   $t = New-ScheduledTaskTrigger -Daily -At 18:00
#   $s = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -ExecutionTimeLimit (New-TimeSpan -Hours 4)
#   Register-ScheduledTask -TaskName "foundation-forecast registry" -Action $a -Trigger $t -Settings $s

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
New-Item -ItemType Directory -Force (Join-Path $repo "registry") | Out-Null
$log = Join-Path $repo "registry\job.log"

function Write-Log([string]$msg) {
    "$((Get-Date).ToString('s')) $msg" | Add-Content -Path $log -Encoding utf8
}

function Publish-Ledger {
    # Commit the ledger file if it has an uncommitted line (a start that was interrupted after
    # sealing), then push. Only ever pushes when the ledger file is the ONLY thing that differs
    # from the remote, so no other local commit is published by this job.
    $dirty = git status --porcelain -- ledger/ledger.jsonl
    if ($dirty) {
        git add -- ledger/ledger.jsonl
        git commit -q -m "ledger: update" -- ledger/ledger.jsonl
        if ($LASTEXITCODE -ne 0) { Write-Log "COMMIT FAILED"; return $false }
        Write-Log "ledger committed"
    }
    git fetch -q origin 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Log "FETCH FAILED: cannot reach the remote; will retry"; return $false }
    $files = @(git diff --name-only "origin/main..HEAD")
    if ($files.Count -eq 0) { return $true }
    if (@($files | Where-Object { $_ -ne "ledger/ledger.jsonl" }).Count -gt 0) {
        Write-Log "NOT PUSHED: other local commits are ahead of the remote; the owner pushes"
        return $false
    }
    git push -q origin HEAD:main
    if ($LASTEXITCODE -ne 0) { Write-Log "PUSH FAILED: ledger commit stays local; will retry"; return $false }
    Write-Log "ledger pushed"
    return $true
}

try {
    # A status that failed to run (seen 2026-11-22 under machine-wide memory pressure) must not
    # read as "nothing due": fail visibly instead, and the next start tries again.
    $raw = uv run ffcast registry-status 2>> (Join-Path $repo "registry\job_run.log")
    $code = $LASTEXITCODE
    $st = if ($raw) { ($raw | Select-Object -Last 1) | ConvertFrom-Json } else { $null }
    if ($code -ne 0 -or $null -eq $st -or $null -eq $st.PSObject.Properties["due"]) {
        Write-Log "STATUS FAILED (exit $code): registry-status gave no usable answer; see registry\job_run.log; will retry at the next start"
        exit 6
    }
    if (-not $st.due) {
        $pushed = Publish-Ledger
        Write-Log "nothing due (enabled=$($st.enabled) preregistered=$($st.preregistered) origin=$($st.origin) done=$($st.done))"
        if ($pushed) { exit 0 } else { exit 4 }
    }
    Write-Log "run due: origin $($st.origin), $($st.days_late) day(s) after the origin day"

    # a live run needs a clean tree: commit a ledger line that is not committed yet (for example
    # line 0, written by registry-init earlier the same day)
    if (git status --porcelain -- ledger/ledger.jsonl) {
        git add -- ledger/ledger.jsonl
        git commit -q -m "ledger: update" -- ledger/ledger.jsonl
        if ($LASTEXITCODE -ne 0) { Write-Log "COMMIT FAILED before the run"; exit 3 }
        Write-Log "ledger committed before the run"
    }

    uv run ffcast registry-run $st.origin *>> (Join-Path $repo "registry\job_run.log")
    if ($LASTEXITCODE -ne 0) { Write-Log "RUN FAILED (exit $LASTEXITCODE); see registry\job_run.log; will retry at the next start"; exit 1 }
    Write-Log "run sealed: origin $($st.origin)"

    uv run ffcast registry-verify *>> (Join-Path $repo "registry\job_run.log")
    if ($LASTEXITCODE -ne 0) { Write-Log "VERIFY FAILED after sealing; ledger not pushed"; exit 2 }
    Write-Log "verified"

    $backup = Join-Path $PSScriptRoot "registry_backup.ps1"
    $backupOk = $true
    if (Test-Path $backup) {
        & $backup
        if ($LASTEXITCODE -ne 0) { Write-Log "BACKUP FAILED (exit $LASTEXITCODE)"; $backupOk = $false } else { Write-Log "backup done" }
    } else {
        Write-Log "no backup script (scripts\registry_backup.ps1): backup skipped"
    }

    $pushed = Publish-Ledger
    if ($pushed -and $backupOk) { Write-Log "done: origin $($st.origin)"; exit 0 }
    if (-not $pushed) { exit 4 }
    exit 5
}
catch {
    Write-Log "JOB ERROR: $($_.Exception.Message)"
    exit 9
}
