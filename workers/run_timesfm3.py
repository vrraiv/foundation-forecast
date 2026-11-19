"""TimesFM 3.0 worker. Univariate or multivariate (all variates as joint targets with variate
attention; variate 0 returned, as for TiRex-2). Quantiles are the model's fixed decile heads;
requested levels must be a subset of 0.1..0.9. The point forecast of this model is its median
head, so no separate mean is returned. Inference options are the package defaults, passed
explicitly so the request records them."""

import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from _common import load_request, run_tasks, setup_torch, versions, write_response  # noqa: E402

req = load_request(sys.argv)
torch = setup_torch(req["settings"])
import numpy as np  # noqa: E402
import timesfm  # noqa: E402

s = req["settings"]
model = timesfm.TimesFM3Forecaster.from_pretrained(
    req["weights_dir"], device="cpu", local_files_only=True
)
max_ctx = int(s.get("max_context", 512))
LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
if [round(float(q), 1) for q in model.config.quantiles] != LEVELS:
    sys.exit(f"unexpected quantile heads in checkpoint: {model.config.quantiles}")


def forecast(task):
    hist = np.asarray(task["history"], dtype=np.float32)[:, -max_ctx:]  # (n_variates, T)
    horizon = int(task["horizon"])
    out = model.predict(
        hist,
        horizon,
        return_quantiles=True,
        use_symmetric_averaging=bool(s.get("use_symmetric_averaging", False)),
        make_positive=bool(s.get("make_positive", False)),
        sort_quantiles=bool(s.get("sort_quantiles", True)),
        use_znorm=bool(s.get("use_znorm", False)),
        padding_mode=str(s.get("padding_mode", "none")),
    )
    q = np.asarray(out.quantiles)  # (n_variates, horizon, 9)
    if q.shape != (hist.shape[0], horizon, len(LEVELS)):
        raise ValueError(f"unexpected output shape {q.shape}")
    idx = [LEVELS.index(round(x, 1)) for x in task["quantiles"]]
    return q[0][:, idx], None


results, errors = run_tasks(req, forecast)
write_response(sys.argv, req, results, errors, versions("timesfm", "torch"))
