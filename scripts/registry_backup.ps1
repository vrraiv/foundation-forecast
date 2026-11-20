# Encrypted backup of the git-ignored work to the project's restic repository (a folder that the
# OneDrive client syncs). Called by scripts/registry_job.ps1 after every registry run; can be run
# by hand at any time. Settings: see scripts/restic.ps1.
#
# What is backed up:
#   registry/   everything. It cannot be rebuilt: the per-origin data snapshots are the only
#               record of what was public on each run day, and the salts are needed for every
#               proof against the public ledger.
#   data/       everything except data/models/ (model weights: re-downloadable at pinned
#               revisions and verified by hash).
# Not backed up: virtual environments (rebuilt from the lockfiles), anything tracked by git.
#
# restic encrypts on this machine before anything is written to the OneDrive folder, compresses,
# and stores unchanged content once. After the backup the repository's structure is checked.
# Exit code 0 only if both the backup and the check succeeded.

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
$restic = Join-Path $PSScriptRoot "restic.ps1"

$paths = @("registry", "data") | Where-Object { Test-Path $_ }
& pwsh -NoProfile -File $restic backup @paths `
    --exclude "data/models" `
    --exclude "**/*.tmp" `
    --tag "foundation-forecast" `
    --host "foundation-forecast"
if ($LASTEXITCODE -ne 0) { Write-Output "BACKUP FAILED (restic exit $LASTEXITCODE)"; exit 1 }

& pwsh -NoProfile -File $restic check
if ($LASTEXITCODE -ne 0) { Write-Output "REPOSITORY CHECK FAILED (restic exit $LASTEXITCODE)"; exit 2 }
exit 0
