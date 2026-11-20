# restic for THIS project's backup repository, and no other.
#
#   pwsh scripts/restic.ps1 snapshots
#   pwsh scripts/restic.ps1 check
#   pwsh scripts/restic.ps1 restore latest --target C:\some\scratch\folder
#
# The repository and the password come from project-specific user environment variables, never
# from the generic RESTIC_* names, so this cannot touch another project's repository by accident:
#   FFCAST_RESTIC_REPOSITORY      folder of the repository (synced to OneDrive by the client)
#   FFCAST_RESTIC_PASSWORD_FILE   path of a file holding the password, or
#   FFCAST_RESTIC_PASSWORD        the password itself
# They are read from the user's Windows profile, so a variable set after this terminal was opened
# is still found. Any generic RESTIC_REPOSITORY / RESTIC_PASSWORD* in the environment is ignored.

$ErrorActionPreference = "Stop"

function Get-Setting([string]$name) {
    $v = [Environment]::GetEnvironmentVariable($name, "User")
    if (-not $v) { $v = [Environment]::GetEnvironmentVariable($name, "Process") }
    return $v
}

$repo = Get-Setting "FFCAST_RESTIC_REPOSITORY"
$pwFile = Get-Setting "FFCAST_RESTIC_PASSWORD_FILE"
$pw = Get-Setting "FFCAST_RESTIC_PASSWORD"
if (-not $repo) { Write-Error "FFCAST_RESTIC_REPOSITORY is not set"; exit 64 }
if (-not $pwFile -and -not $pw) {
    Write-Error "neither FFCAST_RESTIC_PASSWORD_FILE nor FFCAST_RESTIC_PASSWORD is set"
    exit 64
}
if ($pwFile -and -not (Test-Path $pwFile)) { Write-Error "password file not found: $pwFile"; exit 64 }

# only this process sees these; the generic names are cleared first
foreach ($n in "RESTIC_REPOSITORY", "RESTIC_PASSWORD", "RESTIC_PASSWORD_FILE", "RESTIC_PASSWORD_COMMAND") {
    Remove-Item "Env:$n" -ErrorAction SilentlyContinue
}
$env:RESTIC_REPOSITORY = $repo
if ($pwFile) { $env:RESTIC_PASSWORD_FILE = $pwFile } else { $env:RESTIC_PASSWORD = $pw }

& restic @args
exit $LASTEXITCODE
