"""
Optional semantic layer: BAAI/bge-small-en-v1.5 (MIT) via fastembed (Apache-2.0, ONNX, CPU-only).
Loads in a background thread so the UI starts instantly. If it can't load, the app still works
with taxonomy matching only.
"""
import os
import threading

import numpy as np

MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
_model = None
_error = None
_ready = threading.Event()
_started = False


def _load():
    global _model, _error
    try:
        from fastembed import TextEmbedding
        m = TextEmbedding(model_name=MODEL_NAME)
        list(m.embed(["warm up"]))
        _model = m
    except Exception as e:  # network, disk or runtime problems
        _error = f"{type(e).__name__}: {e}"
    finally:
        _ready.set()


def start():
    global _started
    if not _started and os.getenv("DISABLE_EMBEDDINGS") != "1":
        _started = True
        threading.Thread(target=_load, daemon=True).start()


class _Encoder:
    def encode(self, texts):
        arr = np.asarray(list(_model.embed(list(texts))), dtype=np.float32)
        arr /= (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-9)
        return arr


def get(wait: float = 25.0):
    """Return an encoder, waiting up to `wait` seconds for the first load."""
    if not _started:
        return None
    _ready.wait(wait)
    return _Encoder() if _model is not None else None


def status() -> str:
    if not _started:
        return "off"
    if not _ready.is_set():
        return "loading"
    return "ready" if _model is not None else "unavailable"
