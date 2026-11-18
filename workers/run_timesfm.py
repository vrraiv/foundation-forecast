"""TimesFM 2.5 worker (univariate). Quantiles are the model's fixed decile heads; requested
levels must be a subset of 0.1..0.9."""

import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from _common import load_request, run_tasks, setup_torch, versions, write_response  # noqa: E402

req = load_request(sys.argv)
torch = setup_torch(req["settings"])
import numpy as np  # noqa: E402
import timesfm  # noqa: E402

s = req["settings"]
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(req["weights_dir"])
max_ctx = int(s.get("max_context", 512))
model.compile(
    timesfm.ForecastConfig(
        max_context=max_ctx,
        max_horizon=int(s.get("max_horizon", 12)),
        normalize_inputs=bool(s.get("normalize_inputs", True)),
        use_continuous_quantile_head=bool(s.get("use_continuous_quantile_head", True)),
        force_flip_invariance=bool(s.get("force_flip_invariance", True)),
        infer_is_positive=bool(s.get("infer_is_positive", False)),
        fix_quantile_crossing=bool(s.get("fix_quantile_crossing", True)),
    )
)
LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def forecast(task):
    y = np.asarray(task["history"][0], dtype=np.float32)[-max_ctx:]
    point, quant = model.forecast(horizon=int(task["horizon"]), inputs=[y])
    quant = np.asarray(quant)[0]  # (horizon, 10): col 0 mean, cols 1..9 deciles
    idx = [LEVELS.index(round(q, 1)) + 1 for q in task["quantiles"]]
    return quant[:, idx], np.asarray(point)[0]


results, errors = run_tasks(req, forecast)
write_response(sys.argv, req, results, errors, versions("timesfm", "torch"))
