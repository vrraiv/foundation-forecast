# Amendments to the pre-registration

`PREREGISTRATION.md` (ledger line 0, SHA-256
`68479cfc1edd7792bf341e21428ba64b85a122c6c6e37755147c9cf677066075`) is never edited. Each
amendment below is dated and justified. It applies from the first run whose manifest carries the
hash of this file, unless it says otherwise. Forecasts already made are never recomputed or
replaced.

## Amendment 1 (2026-11-26): live forecasts are disclosed; the project computes no live score early

**Applies from:** the 2026-12-25 run. Item 1.4 also covers the run already sealed for 2026-11-25.

**Reason.** The owner's position on disclosure changed after the freeze: direct model outputs
may now be public, ahead of the outturns. The change has nothing to do with any forecast value,
score or outturn. No live forecast has been scored. On the date of this amendment no horizon-1
outturn exists for the one sealed origin, so none could have been. Disclosing forecasts before
their outturns also makes the record stronger: anyone can see the forecast before the outcome is
known, as well as check it against a hash that was public first.

**1.1 Replaces the last two sentences of the "Publicly" paragraph of §7.** Old text: "No forecast
value, score or data value is public, and the salt prevents confirming a guessed forecast file
from its hash." New text:

> After each run's ledger line has been appended and time-stamped, the following are published
> as soon as practicable, as assets of a GitHub release of the public repository tagged
> `registry-<origin>`, byte-identical to the sealed files: `manifest.json`, `salt.hex`,
> `forecasts.parquet`, `status.parquet`, and the time-stamp proof (the time-stamped file and its
> OpenTimestamps proof). They are published with a plain-text export of the forecasts (CSV)
> derived from `forecasts.parquet`; the parquet file is the record and the CSV is a convenience
> copy. With these files anyone can recompute the manifest hash, check it against the ledger line,
> and check the salted commitments against the published forecast and status files. Data
> snapshots stay private; a data value appears in public only where it is a field of a published
> file (see 1.3). Scores are public only under §9 as amended.

**1.2 Replaces the first bullet of §9.** Old text: "...Until then no score, error or ranking is
computed from the live forecasts, by anyone, for any purpose; the forecast files are opened only
by `registry-verify`." New text:

> **No scoring by the project before the record is long enough.** The live record is first scored
> when at least 12 monthly origins have first-release outturns at horizon 1 for every monthly
> target. Until then the project (the owner, the code in this repository, and anyone working on
> it at the owner's request) computes, reports and displays no score, error or ranking from the
> live forecasts, and the public site shows forecasts and outturns but no error, score or
> ranking. The forecast files may be read in order to publish and display them. Once forecasts
> are public, third parties can compute errors themselves; the project neither prevents this nor
> cites, reports or reacts to such computations before its own first scoring.

**1.3 Fields of the status file.** `status.parquet` contains, per series, `last_period`,
`last_level` and `n_history`: the date and value of the last observation in the information set.
These are values from public national sources, already public at the origin, and they are
published with the status file.

**1.4 Origins sealed before this amendment.** The 2026-11-25 run was sealed with
`amendments_sha256: null`. Disclosure changes no sealed file and no forecast, so it does not
affect that run's design. Its files are published under 1.1 once this amendment is committed to
the public repository.

**1.5 Unchanged.** Every other section, including the scoring statistics, the outturn
definitions, the 12-origin threshold, its repetition rule and the no-exclusion rule, stands as
written.
