"""Moirai 2.0 worker (univariate). Moirai 2.0 is a quantile-output model: the gluonts
QuantileForecast carries its decile heads directly; no sampling is involved."""

import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
from _common import load_request, run_tasks, setup_torch, versions, write_response  # noqa: E402

req = load_request(sys.argv)
torch = setup_torch(req["settings"])
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from gluonts.dataset.pandas import PandasDataset  # noqa: E402
from uni2ts.model.moirai2 import Moirai2Forecast, Moirai2Module  # noqa: E402

s = req["settings"]
module = Moirai2Module.from_pretrained(req["weights_dir"])
max_ctx = int(s.get("max_context", 512))
_predictors = {}


def predictor_for(context_length, horizon):
    key = (context_length, horizon)
    if key not in _predictors:
        m = Moirai2Forecast(
            module=module,
            prediction_length=horizon,
            context_length=context_length,
            target_dim=1,
            feat_dynamic_real_dim=0,
            past_feat_dynamic_real_dim=0,
        )
        _predictors[key] = m.create_predictor(batch_size=1)
    return _predictors[key]


def forecast(task):
    y = np.asarray(task["history"][0], dtype=np.float32)[-max_ctx:]
    freq = "M" if task["freq"] == "M" else "Q"
    idx = pd.period_range(
        "2000-01", periods=len(y), freq=freq
    )  # placeholder calendar; model is calendar-free
    ds = PandasDataset(pd.DataFrame({"target": y}, index=idx), target="target")
    torch.manual_seed(int(s.get("seed", 0)))
    fc = next(iter(predictor_for(len(y), int(task["horizon"])).predict(ds)))
    q = np.stack([fc.quantile(float(lv)) for lv in task["quantiles"]], axis=1)  # (horizon, n_q)
    return q, fc.mean


results, errors = run_tasks(req, forecast)
write_response(sys.argv, req, results, errors, versions("uni2ts", "torch", "gluonts"))
