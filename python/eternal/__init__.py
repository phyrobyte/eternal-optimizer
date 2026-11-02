"""Eternal: a causal black-box optimizer. See README.en.md for usage."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from ._core import Memory, Options, _Optimizer, _RandomSearch

__all__ = ["Optimizer", "RandomSearch", "Options", "Memory", "Result", "minimize"]
__version__ = "0.1.0"

Bounds = Union[Mapping[str, Tuple[float, float]], Sequence[Tuple[str, float, float]]]


def _normalize(bounds: Bounds) -> List[Tuple[str, float, float]]:
    if isinstance(bounds, Mapping):
        items = [(str(k), float(v[0]), float(v[1])) for k, v in bounds.items()]
    else:
        items = [(str(n), float(lo), float(hi)) for n, lo, hi in bounds]
    names = [n for n, _, _ in items]
    if len(set(names)) != len(names):
        raise ValueError("parameter names must be unique")
    return items


class Optimizer:
    """Ask/tell causal optimizer. Minimizes; negate the objective to maximize.

    bounds: {"name": (lo, hi), ...} or [("name", lo, hi), ...]
    seed: random seed
    options: eternal.Options() to tune the loop (defaults are what the benchmarks use)
    memory: an eternal.Memory from earlier, related studies; it only proposes, every remembered
            verdict is re-tested by intervention
    """

    def __init__(self, bounds: Bounds, seed: int = 0, options: Optional[Options] = None,
                 memory: Optional[Memory] = None):
        self._params = _normalize(bounds)
        self._names = [n for n, _, _ in self._params]
        self._core = _Optimizer(self._params, seed, options or Options(), memory)

    def ask(self) -> Dict[str, float]:
        """The next point to measure. Calling it again before tell() returns the same point."""
        return dict(zip(self._names, self._core.ask()))

    def tell(self, y: float) -> None:
        """Report the measured value of the last asked point."""
        y = float(y)
        if not math.isfinite(y):
            raise ValueError(f"objective returned {y}; use a large finite penalty for failed evaluations")
        self._core.tell(y)

    def remember(self, previous: Optional[Memory] = None, forget_half_life: float = 0.0) -> Memory:
        """Fold this study into a Memory to warm-start the next related study."""
        return self._core.remember(previous, forget_half_life)

    @property
    def names(self) -> List[str]:
        return list(self._names)

    @property
    def best(self) -> float:
        """Best observed value; inf before the first tell()."""
        return self._core.best if self._core.trials else math.inf

    @property
    def best_params(self) -> Dict[str, float]:
        return dict(zip(self._names, self._core.incumbent))

    @property
    def has_memory(self) -> bool:
        return self._core.has_memory

    @property
    def noise(self) -> float:
        """Estimated measurement noise (standard deviation)."""
        return self._core.noise

    @property
    def verdicts(self) -> List[Dict[str, Any]]:
        """Per parameter: whether it was tested, judged a cause, its effect size and signal/noise."""
        return self._core.verdicts

    @property
    def causes(self) -> List[str]:
        return [v["name"] for v in self._core.verdicts if v["tested"] and v["cause"]]

    @property
    def frozen(self) -> List[str]:
        """Parameters judged irrelevant and fixed at the incumbent's value."""
        return [v["name"] for v in self._core.verdicts if v["tested"] and not v["cause"]]

    @property
    def trials(self) -> List[Dict[str, Any]]:
        return self._core.trials

    @property
    def events(self) -> List[Dict[str, Any]]:
        """Freezes, revivals, zooms and expansions, in order."""
        return self._core.events

    @property
    def pending_kind(self) -> str:
        """Why the pending point was proposed: warmup, remeasure, intervene, exploit, explore, local, random or recall."""
        return self._core.pending_kind

    def __repr__(self) -> str:
        return f"<eternal.Optimizer params={self._names} trials={len(self._core.trials)} best={self.best:g}>"


class RandomSearch:
    """Uniform random search with the same interface, as a baseline."""

    def __init__(self, bounds: Bounds, seed: int = 0):
        self._params = _normalize(bounds)
        self._names = [n for n, _, _ in self._params]
        self._core = _RandomSearch(self._params, seed)
        self._told = False

    def ask(self) -> Dict[str, float]:
        return dict(zip(self._names, self._core.ask()))

    def tell(self, y: float) -> None:
        y = float(y)
        if not math.isfinite(y):
            raise ValueError(f"objective returned {y}; use a large finite penalty for failed evaluations")
        self._told = True
        self._core.tell(y)

    @property
    def best(self) -> float:
        """Best observed value; inf before the first tell()."""
        return self._core.best if self._told else math.inf


@dataclass
class Result:
    best: float
    best_params: Dict[str, float]
    causes: List[str]
    frozen: List[str]
    trials: List[Dict[str, Any]] = field(repr=False)
    optimizer: Optimizer = field(repr=False)


def minimize(f: Callable[..., float], bounds: Bounds, budget: int = 200, seed: int = 0,
             options: Optional[Options] = None, memory: Optional[Memory] = None) -> Result:
    """Minimize f(**params) within bounds using `budget` evaluations."""
    if budget < 1:
        raise ValueError("budget must be at least 1")
    opt = Optimizer(bounds, seed=seed, options=options, memory=memory)
    for _ in range(budget):
        x = opt.ask()
        opt.tell(f(**x))
    return Result(opt.best, opt.best_params, opt.causes, opt.frozen, opt.trials, opt)
