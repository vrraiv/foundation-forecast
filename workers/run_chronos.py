"""Chronos-2 worker. Univariate: history has one variate. Multivariate: all variates are
forecast jointly and the target's (variate 0) quantiles are returned."""

import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from _common import load_request, run_tasks, setup_torch, versions, write_response  # noqa: E402

req = load_request(sys.argv)
torch = setup_torch(req["settings"])
import numpy as np  # noqa: E402
from chronos import BaseChronosPipeline  # noqa: E402

pipe = BaseChronosPipeline.from_pretrained(
    req["weights_dir"], device_map="cpu", torch_dtype=torch.float32
)
max_ctx = int(req["settings"].get("max_context", 512))


def forecast(task):
    hist = np.asarray(task["history"], dtype=np.float32)  # (n_variates, T)
    hist = hist[:, -max_ctx:]
    x = torch.tensor(hist).unsqueeze(0)  # (1, n_variates, T)
    q, mean = pipe.predict_quantiles(
        x, prediction_length=int(task["horizon"]), quantile_levels=task["quantiles"]
    )
    q = q[0] if isinstance(q, list) else q
    mean = mean[0] if isinstance(mean, list) else mean
    q = q.numpy()
    mean = mean.numpy()
    # shapes: (n_variates, horizon, n_q) or (horizon, n_q) for a single series
    if q.ndim == 3:
        q, mean = q[0], mean[0]
    return q, mean


results, errors = run_tasks(req, forecast)
write_response(
    sys.argv, req, results, errors, versions("chronos-forecasting", "torch", "transformers")
)
