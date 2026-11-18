"""TiRex (v1) worker, univariate, CPU. Fixed decile quantiles 0.1..0.9."""

import os
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
os.environ.setdefault("TIREX_NO_CUDA", "1")
from _common import load_request, run_tasks, setup_torch, versions, write_response  # noqa: E402

req = load_request(sys.argv)
torch = setup_torch(req["settings"])
import glob  # noqa: E402

import numpy as np  # noqa: E402
from tirex.base import PretrainedModel  # noqa: E402

# tirex.load_model only accepts a Hugging Face repo id; its from_pretrained accepts a local
# checkpoint file, so the pinned snapshot is loaded through the registry directly.
ckpt = sorted(glob.glob(req["weights_dir"] + "/*.ckpt"))[0]
model = PretrainedModel.REGISTRY["TiRex"].from_pretrained(
    ckpt, backend="torch", device="cpu", compile=False
)
max_ctx = int(req["settings"].get("max_context", 512))
LEVELS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def forecast(task):
    y = np.asarray(task["history"][0], dtype=np.float32)[-max_ctx:]
    q, mean = model.forecast(
        context=torch.tensor(y).unsqueeze(0), prediction_length=int(task["horizon"])
    )
    q = q[0].numpy()  # (horizon, 9)
    idx = [LEVELS.index(round(x, 1)) for x in task["quantiles"]]
    return q[:, idx], mean[0].numpy()


results, errors = run_tasks(req, forecast)
write_response(sys.argv, req, results, errors, versions("tirex", "torch"))
