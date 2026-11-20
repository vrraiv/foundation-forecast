# Live registry (Phase 5)

Purpose: a forecast record that can later be proven to have existed at each date, without
publishing the forecasts. What the record contains and how it will be scored is fixed in
`PREREGISTRATION.md`; this file describes the machinery, the trial run, and the two proposals
the plan asks for (backup, scheduling). State on 2026-11-19: the registry is enabled in the
configuration and the scheduled task is registered, on the owner's instruction, but no live run
can happen until the owner has approved the pre-registration text and `ffcast registry-init` has
hashed it into ledger line 0.

## Commands

    uv run ffcast registry-init                 # entry 0: hash of PREREGISTRATION.md
    uv run ffcast registry-run [YYYY-MM-DD]     # one origin: snapshot, forecast, seal, ledger entry
    uv run ffcast registry-verify [--recompute YYYY-MM-DD]

All three take `--root` (and `--ledger`) to work in a scratch folder; `registry-run --dry-run`
requires one. A live run additionally requires `registry.enabled: true`, a clean working tree
and a pre-registration entry in the ledger. An origin in the future, a date that is not an
origin, and an origin already in the ledger are refused.

## What a run does

1. **Snapshot.** The data pipeline of `ffcast data` downloads every source into
   `registry/origins/<origin>/snapshot/raw` and writes the normalised change-log tables to
   `.../snapshot/normalised`. The backtest's `data/normalised` is never touched (its file hashes
   are in every backtest cache key). About 0.6 GB per origin, mostly OECD editions and the ECB
   real-time database.
2. **Forecast.** Two information sets from the one snapshot (`PREREGISTRATION.md`, section 3):
   `realtime`, the backtest rule at the origin, and `live`, everything public at the run. Both go
   through the backtest's own functions (`stage1_origin` for panels, benchmarks and task
   building, the worker processes, `stage3` for parsing and the validity guard); `live` mode
   feeds them a re-dated copy of the snapshot table and a config whose targets point at the
   national series (`ffcast.registry.live`). No second panel builder exists. Models: the active
   foundation models only (`Config.active_foundation_models()`), so a retired model never runs.
3. **Seal.** `forecasts.parquet` and `status.parquet` are written with fixed column order, sorted
   rows, no timestamps, runtimes or cache keys, and no writer metadata, so the bytes depend only
   on the values. A 256-bit salt is drawn from the operating system. The configuration and the
   lockfiles (root and each active model environment) are copied to `pins/`. `manifest.json`
   records the origin, run time (UTC), lateness, code commit, design hash, pre-registration
   hash, the salted commitments `SHA-256(salt || file)` to both parquet files, the snapshot
   digest (SHA-256 over the sorted list of every snapshot file's path and hash), the pins'
   hashes and each model's weights digest.
4. **Ledger.** One line is appended to `ledger/ledger.jsonl`: sequence number, kind, origin,
   SHA-256 of the manifest file, the time of appending (UTC), the previous line's hash, and the
   line's own hash.
   The line is then time-stamped (`registry.opentimestamps`: `stub` writes a placeholder and
   contacts nobody; `ots` obtains an OpenTimestamps proof). In `ots` mode the line's hash is
   written to a small text file and a standard `.ots` proof is stored next to it. What is sent
   to the public calendar servers is one 32-byte value: the SHA-256 of that file's hash followed
   by a random nonce, so not even the line's hash leaves the machine. The proof starts as a
   calendar commitment and can be upgraded to a Bitcoin attestation and checked later with any
   OpenTimestamps client or the opentimestamps.org page, using the text file and the `.ots`
   file. The reference command-line client does not run on Windows (its Bitcoin library fails
   to load OpenSSL), so the registry uses the client's library (`opentimestamps` 0.5.0, in the
   root lockfile) directly. Tested once on 2026-11-19 with the trial entry's hash: accepted by
   all three default calendars, 584-byte proof, proof check passes.

Private layout (`registry/` is git-ignored):

    registry/prereg/PREREGISTRATION.md        the text as hashed, plus proofs/
    registry/origins/<origin>/snapshot/       raw downloads and normalised tables
    registry/origins/<origin>/forecasts.parquet, status.parquet, salt.hex, manifest.json
    registry/origins/<origin>/pins/           config and lockfiles used
    registry/origins/<origin>/proofs/         time-stamp proof of the ledger line
    registry/origins/<origin>/work/           worker requests and responses (not hashed)

Public: `ledger/ledger.jsonl` only. It contains dates and hashes. The salt keeps a guessed
forecast file from being confirmed against the ledger; the manifest itself is private because it
lists counts of failed models and data problems, which are forecast-adjacent.

## Verify

`registry-verify` reports a problem if any of these fails: the chain (sequence, each `prev`, each
line's own hash, the first line being the pre-registration, one line per origin); the private
copy of the pre-registration against line 0; for every run line, the manifest against the
ledger, the forecast and status files against the salted commitments, the snapshot against its
digest, the pinned files against their hashes, the local weights against the digests where the
weights are present, the time-stamp proof or placeholder against the line's hash; and a sealed
origin on disk that has no ledger line (a truncated ledger). `--recompute` reruns one origin
from its stored snapshot and pinned configuration and compares both files byte for byte.

Tests (`tests/test_registry.py`, synthetic files, no model and no network): a clean registry
verifies; 17 kinds of tampering each make it fail (forecast, status, snapshot edit and added
file, manifest, salt, pinned lockfile, pre-registration text, a ledger field, a ledger line
rewritten with a fresh hash, a removed middle line, a removed last line, reordered lines, a
deleted forecast file, a deleted origin, forecast files swapped between origins, a removed
proof); the ledger refuses a second line for an origin, a second pre-registration, and a run
before the pre-registration; live runs are refused before Gate 5; the forecast file's bytes do
not depend on row order; the plain hash of the forecast file appears in neither manifest nor
ledger; `live` mode joins the national series to the vintage history as specified; an interrupted run
is completed without touching sealed files; and an overtaken origin is refused.

What the machinery cannot prove by itself: that an entry existed at its date. That is what the
independent time stamps are for (approved by the owner on 2026-11-19; switched on with the
registry) together with the public git history of the ledger. `registry-verify` checks that
each proof belongs to its ledger line and carries an attestation; it does not check the Bitcoin
attestation itself, which any OpenTimestamps client can do once the proof has been upgraded.

## Trial run

Run on 2026-11-19 in a scratch folder (`data/registry_trial_20261119/`, git-ignored), with a
placeholder pre-registration, time-stamping on `stub`, origin 2026-10-26. The origin had passed,
so this was also a test of the late-run rule. No forecast value was read or printed; only
statuses, dates and hashes were inspected.

- **First attempt failed, usefully.** After 32 minutes of downloading, the ECB data service
  timed out and the unhandled network error ended the run. Nothing had been sealed and the
  ledger still held only the placeholder entry. Fix: every download now gets three attempts
  (waits of 10 and 40 seconds; network errors, HTTP 429 and 5xx); a download that still fails is
  listed, and a run refuses to seal an incomplete snapshot unless `--accept-incomplete` is given,
  in which case the failures go into the manifest. Repeating a run the same day reuses the files
  already downloaded.
- **Second attempt sealed.** 28 minutes, most of it download. Snapshot: 175 files, 76 series,
  576 MB, no failed download. All five model workers ok in both modes. Status rows: 224 ok in
  `realtime`, 228 ok in `live`, none skipped, none in error (the difference is four multivariate
  cells for one target whose balanced panel has a single column under the backtest rule).
  37,872 forecast rows, 280 KB. Manifest: late by 24 days, trial, working tree not clean (the
  Phase 5 code was uncommitted), all recorded.
- **The two information sets differ as designed.** Last observed period of each target,
  `realtime` versus `live`: Canadian CPI and CPI-XFET 2026-09 / 2026-10, unemployment 2026-08 /
  2026-10, retail 2026-06 / 2026-08, GDP and consumption 2026-Q2 in both; euro-area HICP
  2026-08 / 2026-10, core HICP 2026-09 / 2026-10, unemployment and retail 2026-07 / 2026-09,
  GDP 2026-Q2 / 2026-Q3, consumption 2026-Q2 in both. (For a late run `live` uses the run day's
  data, which is why it is reported separately.)
- **Like for like with the backtest.** The backtest store already holds origin 2026-10-26. The
  trial's `realtime` rows, from a fresh download made 24 days after the origin, are identical to
  the store's for that origin: 18,720 of 18,720 rows, same target periods, every benchmark and
  all five models, the pseudo-vintage targets included.
- **Joined history.** Four targets take early history from the vintage source in `live` mode:
  Canadian retail (from 2017-01, 312 earlier months from the OECD), Canadian CPI (1995-01, 420
  months), Canadian unemployment (1976-01, 192 months), euro-area retail (2000-01, 60 months).
- **National series against the vintage sources on their overlap** (largest absolute difference
  of the transformed series): Canadian GDP, consumption and unemployment 0; Canadian retail 0.008
  percentage points over 115 months, joined to the OECD history at 2017-01; Canadian CPI 0.012;
  euro-area GDP and consumption 0.001; HICP 0.010; unemployment 0.1 (one decimal of rounding);
  euro-area retail 0.12, the only pair where the two sources visibly differ.
- **Verification and rerun.** `registry-verify --recompute 2026-10-26` (5 minutes): every ledger
  entry matches its private files, and the rerun from the stored snapshot and pinned
  configuration reproduced `forecasts.parquet` and `status.parquet` byte for byte, with all
  models rerun.

Not exercised by the trial: an on-time run (the next origin is 2026-11-25), the scheduled job,
and a run from a clean committed tree. Real time-stamping was tested separately (step 4 above).

## Proposal: backup (plan step 7)

The owner asked on 2026-11-19 for an encrypted cloud backup of all git-ignored work on their
OneDrive, with restic or similar. Proposal, nothing set up:

- **Tool:** restic with its rclone backend pointed at OneDrive. restic encrypts on this machine
  before upload (the store holds unpublished forecasts), deduplicates (monthly snapshots repeat
  most raw files), and verifies with `restic check`.
- **Scope:** `registry/` in full (it cannot be rebuilt: the snapshots are the only record of
  what was public on each run day, and the salts are needed for every proof) and `data/` except
  `data/models/` (weights are re-downloadable at pinned revisions and verified by hash) and the
  virtual environments (rebuilt from lockfiles). About 5 GB to start, about 0.6 GB per month.
- **When:** after every registry run, as the last step of the scheduled job, and once now for
  `data/`.
- **Password:** in the owner's password manager, not on this machine in a file and not in the
  repository. Without it the backup is unreadable; with only it and OneDrive the registry is
  recoverable.
- **Restore test:** once after setup and once a year: restore to a scratch folder and run
  `registry-verify --root` on it.
- **Owner steps:** create the rclone OneDrive remote (an interactive login), choose the folder,
  choose the password. The agent can write the two-line backup script and the restore test once
  the remote exists.
- A second copy on an external disk would protect against losing access to the account.

## Backup as built (2026-11-19)

Differs from the proposal in one way: no rclone. The repository is an ordinary folder inside
the owner's OneDrive-synced directory, and the OneDrive client uploads it; restic encrypts
before writing, so only ciphertext reaches OneDrive. `scripts/registry_backup.ps1` backs up
`registry/` and `data/` (minus `data/models/`) and runs `restic check`; `scripts/restic.ps1`
runs any restic command against this repository using `FFCAST_RESTIC_REPOSITORY` and
`FFCAST_RESTIC_PASSWORD_FILE` from the user's Windows profile and ignores the generic
`RESTIC_*` variables. First backup 451 MiB stored for 2.5 GiB read (raw OECD and ECB text
compresses to a few percent). Restore test passed: restored copies of the trial run and of
`registry/` verify with `registry-verify`, and the restored trial equals the original file
for file. To restore after a loss: install restic, point the two variables at the repository
folder and a file holding the password, `pwsh scripts/restic.ps1 restore latest --target <dir>`,
then `ffcast registry-verify --root <dir>/registry`.

## Proposal: scheduling (plan step 8; not enabled)

Requirement: one run on each origin day, at a fixed time, with an alert on failure, and no run
that silently does not happen.

| Option | How | For | Against |
|---|---|---|---|
| A. Windows Task Scheduler on this machine | A task on the 25th to 28th at 18:00 that runs `ffcast registry-run` only if today is the origin day or the origin was missed, then the backup, then pushes the ledger | Models, weights, environments and the private store are already here; nothing private leaves the machine; no cost | The machine must be on and awake; memory pressure has stopped jobs here before (one origin needs far less than the backtest did); a failure is only seen if the alert works |
| B. Scheduled workflow in a private repository (GitHub Actions) | Monthly cron; the runner downloads data and weights, runs, and stores the private files as an encrypted artifact or pushes them to private storage | Independent of this machine; the run time is recorded by a third party | The private forecasts and salts would live on a third-party service, against "forecasts are private" unless encrypted with a key held in the service's secrets; 1.3 GB of weights and six environments per run; Statistics Canada blocked scripted access from a GitHub runner on 2026-11-18 (36 attempts, all refused) and the fix reported on 2026-11-19 has not been tested from there; cron on hosted runners can be delayed |
| C. A plus a monthly reminder | Option A, and a calendar reminder for the owner on the origin day to look at the tracker | Covers the main weakness of A at no cost | Relies on the owner once a month |

Recommendation: **C**. The run is light (one origin), everything it needs is on this machine,
and the late-run rule turns a missed evening into a recorded late run instead of a gap.

Failure handling, for any option:

- The job writes a one-line result (ok, late by n days, failed with the reason) to a log and
  updates the tracker artifact; on failure it also raises a Windows notification. An e-mail alert
  is possible but needs an account the owner chooses.
- A run that fails before sealing leaves no ledger line and can simply be repeated the same day.
  The order of the last writes is: sealed files and manifest, then the ledger line, then the
  time stamp (which needs the network once real stamping is on). A run interrupted between them
  is finished by repeating `registry-run` for that origin: it finds the sealed manifest, appends
  the missing line or requests the missing stamp, and changes no sealed file (tested).
- Late rule: as in `PREREGISTRATION.md`, section 2. The job retries on the following days of the
  same month; each attempt after the origin day is a late run and says so in its manifest.
- Pushing the ledger: one commit per origin containing only `ledger/ledger.jsonl`. Whether the
  job pushes by itself or the owner pushes is the owner's choice at Gate 5.

## Decided on 2026-11-19 and built (not switched on)

The owner chose option C, the ledger in this repository with its own workflow, and asked for a
fallback because scheduled GitHub workflows in their other repositories sometimes start late or
never. Division of labour:

- **The run is local.** `scripts/registry_job.ps1`, started daily at 18:00 by Windows Task
  Scheduler (registration command in the script's header; "start when available" catches up
  after the machine was off). It asks `ffcast registry-status` whether the current origin is
  done; if not, it runs, verifies, backs up (once `scripts/registry_backup.ps1` exists) and
  publishes the ledger. Because it starts every day, a failed or missed evening is retried the
  next day as a late run, with no separate retry logic. It commits and pushes
  `ledger/ledger.jsonl` only, and refuses to push if any other local commit is ahead of the
  remote, so it can never publish the owner's unpushed work. Tried once with the registry off:
  it logged "nothing due" and changed nothing.
- **GitHub only checks.** `.github/workflows/ledger.yml` never forecasts and never sees private
  data. On every push that touches the ledger it runs `scripts/check_ledger.py` (standard
  library only): the hash chain holds and the file only grew. On a schedule (27th to 3rd, 14:00
  UTC) it also requires a line for every origin that is due, and on failure opens an issue,
  which GitHub mails to the owner.
- **No single alarm is trusted.** (1) The local job retries daily and its failures show in Task
  Scheduler's last result and in `registry/job.log`. (2) The scheduled workflow is tried on up
  to eight days per month, so one skipped or delayed start does not silence it. (3) The owner's
  calendar reminder on the origin day. (4) The time stamp of each line does not depend on
  GitHub at all, so a delayed push does not weaken the proof of date.
- Remaining single point of failure: this machine. If it is unavailable for a whole month, that
  origin is missing from the record and the ledger shows it.

## Not built

- Scoring of the live record (the pre-registration forbids computing any score before 12
  origins have outturns; the code will be the backtest's scoring applied to the registry files).
- Upgrading pending time-stamp proofs to complete Bitcoin attestations and verifying those
  (possible at any later date with public tools; the pending proofs are what must be kept).
- (Backup: built and tested on 2026-11-19, see below.)
- Registering the scheduled task: the owner's step after HUMAN GATE 5.
