# src/utils/generator_debug.py
# Utility functions for debugging the name generator

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


@dataclass
class GenerationAnalysis:
    unique_count: int
    total_count: int
    avg_length: float
    hyphen_count: int
    underscore_count: int
    all_start_with_seed: bool
    empty_count: int
    generation_time_ms: Optional[float] = None
    data_size: Optional[int] = None


def _now_iso() -> str:
    return datetime.now().isoformat()


def _save_json(payload: Dict[str, Any], prefix: str = "generator_debug") -> str:
    """Write payload to logs/<prefix>_<timestamp>.json and return the path as str."""
    LOG_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = LOG_DIR / f"{prefix}_{ts}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return str(path)


def analyze_samples(samples: List[str], seed: str,  generation_time: Optional[float] = None, data_size: Optional[int] = None) -> GenerationAnalysis:
    """Compute simple, stable metrics over a batch of generated strings."""
    if not samples:
        return GenerationAnalysis(
            unique_count=0,
            total_count=0,
            avg_length=0.0,
            hyphen_count=0,
            underscore_count=0,
            all_start_with_seed=False,
            empty_count=0,
            generation_time_ms=None, 
            data_size=data_size,
        )

    if generation_time is not None:
        generation_time_ms = round(generation_time * 1000, 2)
    else:
        generation_time_ms = None

    return GenerationAnalysis(
        unique_count=len(set(samples)),
        total_count=len(samples),
        avg_length=sum(len(s) for s in samples) / len(samples),
        hyphen_count=sum("-" in s for s in samples),
        underscore_count=sum("_" in s for s in samples),
        all_start_with_seed=all(s.startswith(seed) for s in samples if s),
        empty_count=sum(s == "" for s in samples),
        generation_time_ms=generation_time_ms,
        data_size=data_size,
    )


def print_generation_summary(
    k: int,
    seed: str,
    max_length: int,
    samples: List[str],
    *,
    n_requested: Optional[int] = None,
    generation_time: Optional[float] = None,
    log_prefix: str = "generator_debug",
    data_size: Optional[int] = None,
     paths: Optional[List[List[Dict[str, str]]]] = None
) -> str:
    """
    Print a concise summary AND persist a full JSON log in `logs/`.
    Returns the path to the written log file.

    Minimal call from generator:
        print_generation_summary(self.k, seed, max_length, results)

    Optionally pass n_requested (i.e., batch size) or override log_prefix.
    """
    metrics = analyze_samples(samples, seed, generation_time, data_size)
    # Console summary
    print(f"\n----------------------------------(generator debug output)")
    print(f"  Input: k={k}, seed='{seed}', len={max_length}")
    print(f"  Data Size: {metrics.data_size}")
    print(f"  Unique: {metrics.unique_count}/{metrics.total_count}")
    print(f"  Avg length: {metrics.avg_length:.1f}")
    print(f"  Special chars: {metrics.hyphen_count} hyphens, {metrics.underscore_count} underscores")
    if metrics.generation_time_ms is not None:  
        print(f"  Generation time: {metrics.generation_time_ms:.1f}ms")
    print(f"  Examples: {samples[:3]}")
    if paths:
        max_samples_to_show = 2
        max_steps_to_show = 10
        print("  Paths:")
        for i, sample_path in enumerate(paths[:max_samples_to_show]):
            print(f"    Sample {i+1}:")
            for step_idx, step in enumerate(sample_path[:max_steps_to_show]):
                ctx = step.get("context", "")
                ch  = step.get("chosen_char", "")
                print(f"      {step_idx:02d}. [{ctx!r}] -> {ch!r}")
            if len(sample_path) > max_steps_to_show:
                print(f"      ... ({len(sample_path) - max_steps_to_show} more steps)")

    # Persist JSON log
    payload = {
        "timestamp": _now_iso(),
        "k": k,
        "seed": seed,
        "max_length": max_length,
        "n_requested": n_requested,
        "samples": samples,
        "analysis": asdict(metrics),
        "paths": paths,
    }
    path = _save_json(payload, prefix=log_prefix)
    print(f"[debug] log saved → {path}")
    return path