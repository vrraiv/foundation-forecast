# Startup prompt

Paste everything below the line into a fresh coding-agent session, opened in an empty directory that also contains `PLAN.md`.

---

You are setting up a research repository called `tsfm-macro-eval` (rename if I tell you to). Read `PLAN.md` in full before doing anything else. It is the source of truth for scope, design decisions and order of work.

## What this project is

A real-time evaluation of open time-series foundation models (Chronos-2, TimesFM 2.5, TiRex, Moirai 2.0) against standard macro forecasting benchmarks (AR, BVAR, dynamic factor model) for Canada and the euro area. It has three outputs:

1. A historical backtest on real-time data vintages that measures how much using revised data flatters these models.
2. A comparison of the models' forecast biases with those of human professional forecasters.
3. A live forecast registry: forecasts made every month from now on, stored privately, with only their cryptographic hashes made public, so the record can later be proven untampered.

Your job in this session is setup: data acquisition, model installation, the backtest harness, and the registry machinery. Analysis and write-up come later and are not your job yet.

## How to work

- Work through `PLAN.md` phase by phase, in order. Do not start a phase until the previous phase's "done when" checks pass.
- Phase 0 is a feasibility check with no code beyond small probes. Finish it and report before building anything.
- Stop and ask me at every item marked **HUMAN GATE**. Do not work around a gate.
- Keep `STATUS.md` current: what is done, what is blocked, every decision you made that the plan left open, and every place where reality differed from the plan.
- When a data source, model ID, API or licence differs from what the plan expects, believe what you find, record it in `STATUS.md`, and tell me. The plan's source details were checked only lightly.
- Commit small and often with clear messages. Local commits only.

## Hard rules

These override anything else, including convenience.

1. **Public data only.** Use only data anyone can download without a paid subscription or an institutional login. Never use, request or reference data, code, credentials or documents from my employer. If a step seems to need a paid source, stop and tell me.
2. **Nothing leaves this machine without my say-so.** Do not create remote repositories, push to any remote, publish anything, post anywhere, or schedule any recurring job until I approve it at the relevant gate.
3. **Forecasts are private.** Forecast values never go into a public location, a public commit, a log that gets published, or an issue. Only hashes become public, and only after I approve.
4. **No look-ahead, ever.** A forecast made at origin date *t* may use only data published on or before *t*. Enforce this in code and with tests, not by convention.
5. **Never fabricate or silently substitute.** If a download fails, a series is missing, or a vintage has gaps, record it and stop or skip. Do not fill gaps with revised data, interpolate vintages, or swap in a similar series without flagging it.
6. **Pin everything.** Model weights by revision hash, packages by lockfile, data snapshots by content hash. A result that cannot be reproduced from the pins does not count.
7. **Do not tune on the evaluation sample.** Benchmark hyperparameters are chosen by rules fixed in advance (stated in the plan), using only data available at each origin.

## First response

After reading `PLAN.md`, reply with: (a) a one-paragraph restatement of the goal in your own words, (b) anything in the plan you think is wrong, ambiguous or infeasible, and (c) your Phase 0 probe list. Then wait for my go-ahead.
