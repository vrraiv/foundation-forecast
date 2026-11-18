"""TiRex-2 worker. Univariate or multivariate (all variates as joint targets; variate 0 returned).
torch.compile is disabled (no MSVC on Windows); fixed decile quantiles."""

import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from _common import load_request, run_tasks, setup_torch, versions, write_response  # noqa: E402

req = load_request(sys.argv)
torch = setup_torch(req["settings"])
import numpy as np  # noqa: E402
from tirex2 import TimeseriesType, load_model  # noqa: E402

model = load_model(req["weights_dir"], device="cpu", compile=False)
max_ctx = int(req["settings"].get("max_context", 512))
LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def forecast(task):
    hist = np.asarray(task["history"], dtype=np.float32)[:, -max_ctx:]
    ts = TimeseriesType(target=torch.tensor(hist), past_covariates=None, future_covariates=None)
    out = model.forecast([ts], prediction_length=int(task["horizon"]))[0]  # (n_targets, 9, horizon)
    q = out[0].numpy().T  # (horizon, 9)
    idx = [LEVELS.index(round(x, 1)) for x in task["quantiles"]]
    return q[:, idx], None


results, errors = run_tasks(req, forecast)
write_response(sys.argv, req, results, errors, versions("tirex-2", "torch"))
