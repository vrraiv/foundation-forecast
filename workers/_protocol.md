# Worker protocol

Each foundation model runs in its own uv environment (`envs/<env>/`) through a worker script
in this folder. Workers never import `ffcast`; they only see what the orchestrator hands them,
which is the output of `as_of` for one origin. That is how the no-look-ahead rule is enforced
at the process boundary.

Invocation (by `ffcast.models.runner`):

    uv run --project envs/<env> --no-project python workers/run_<env>.py REQUEST.json RESPONSE.json  (scripts are prefixed run_ so they do not shadow the model packages)

Request JSON:

    {
      "model": "chronos2",
      "weights_dir": "data/models/amazon__chronos-2/<sha>",   # local snapshot, loaded offline
      "settings": {...},                                       # from configs/default.yaml
      "tasks": [
        {"id": "CA.gdp.2016-03-25.uni", "freq": "Q",
         "history": [[...]],            # list of variates; variate 0 is the target
         "horizon": 4, "quantiles": [0.1, ..., 0.9]}
      ]
    }

Response JSON:

    {"model": "chronos2", "versions": {...}, "seed": 0, "threads": 4,
     "results": {"<id>": {"quantiles": [[q1..qK] per step], "mean": [...] or null,
                          "runtime_s": 0.12}},
     "errors": {"<id>": "message"}}

Determinism: workers set `torch.manual_seed(settings.seed)`, `torch.set_num_threads(settings.threads)`,
and `HF_HUB_OFFLINE=1`. Sampling-based models record the seed; a rerun with the same request
must produce byte-identical output (checked by the smoke test).
