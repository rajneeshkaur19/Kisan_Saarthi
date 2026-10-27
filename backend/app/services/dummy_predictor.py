""" 
dummy_predictor

A minimal stub used when the original ``ml.predict`` module has been removed.
It provides the same public API expected by the rest of the code‑base:
``get_disease_predictor()`` returns an object with a ``model_loaded`` attribute
that is always ``False`` and a ``demo_mode`` flag set to ``True``.
"""

from dataclasses import dataclass


@dataclass
class _DummyPredictor:
    """Mimic the interface of the original ML predictor."""
    model_loaded: bool = False
    demo_mode: bool = True


def get_disease_predictor() -> _DummyPredictor:
    """Return a deterministic predictor used for demo‑mode responses.

    The real project previously returned an object with a ``model_loaded`` flag.
    Here we always indicate that no model is loaded (because we removed the local
    ML code) and that we are running in demo mode.
    """
    return _DummyPredictor()