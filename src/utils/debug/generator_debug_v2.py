# src/utils/debug/generator_debug_v2.py
"""Debug utilities for generator analysis and logging."""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

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
    similarity: Optional[Dict[str, float]] = None
    consonant_vowel_ratio: Optional[float] = None

def _now_iso() -> str:
    return datetime.now().isoformat()

def levenshtein_distance(a: str, b: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur.append(min(ins, dele, sub))
        prev = cur
    return prev[-1]

def ngram_f1(a: str, b: str, n: int = 3) -> float:
    """Calculate n-gram F1 score between two strings."""
    def _ngrams(s: str, n: int) -> List[str]:
        return [s[i:i+n] for i in range(max(0, len(s) - n + 1))] if s else []
    
    A, B = _ngrams(a, n), _ngrams(b, n)
    if not A and not B:
        return 1.0
    if not A or not B:
        return 0.0
    
    from collections import Counter
    cA, cB = Counter(A), Counter(B)
    inter = sum((cA & cB).values())
    p = inter / max(1, sum(cA.values()))
    r = inter / max(1, sum(cB.values()))
    return 0.0 if (p + r) == 0 else (2 * p * r) / (p + r)

def _save_json(payload: Dict[str, Any], prefix: str = "generator_debug") -> str:
    """Write payload to logs/<prefix>_<timestamp>.json."""
    LOG_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = LOG_DIR / f"{prefix}_{ts}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return str(path)

def analyze_samples(samples: List[str], seed: str, 
                   generation_time: Optional[float] = None, 
                   data_size: Optional[int] = None) -> GenerationAnalysis:
    """Compute metrics over generated samples."""
    if not samples:
        return GenerationAnalysis(
            unique_count=0, total_count=0, avg_length=0.0,
            hyphen_count=0, underscore_count=0,
            all_start_with_seed=False, empty_count=0,
            generation_time_ms=None, data_size=data_size
        )

    generation_time_ms = round(generation_time * 1000, 2) if generation_time else None
    
    # Calculate similarity metrics
    similarity = None
    if seed and samples:
        try:
            levs = [levenshtein_distance(s, seed) for s in samples if s]
            f1s = [ngram_f1(s, seed, n=3) for s in samples if s]
            similarity = {
                "levenshtein_mean": round(sum(levs) / len(levs), 3) if levs else None,
                "ngram_f1_mean": round(sum(f1s) / len(f1s), 3) if f1s else None
            }
        except Exception:
            similarity = None

    # Calculate consonant-to-vowel ratio
    consonant_vowel_ratio = None
    try:
        vowels = set('aeiouAEIOU')
        ratios = []
        for s in samples:
            if not s:
                continue
            # Count only alphabetic characters
            letters = [c for c in s if c.isalpha()]
            if not letters:
                continue
            vowel_count = sum(1 for c in letters if c in vowels)
            consonant_count = len(letters) - vowel_count
            if vowel_count > 0:
                ratios.append(consonant_count / vowel_count)
        
        consonant_vowel_ratio = round(sum(ratios) / len(ratios), 3) if ratios else None
    except Exception:
        consonant_vowel_ratio = None

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
        similarity=similarity,
        consonant_vowel_ratio=consonant_vowel_ratio
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
    paths: Optional[List[List[Dict[str, str]]]] = None,
    config: Optional[Dict[str, Any]] = None,
    continuation_flags: Optional[List[bool]] = None
) -> str:
    """Print summary and save JSON log with full configuration."""
    
    metrics = analyze_samples(samples, seed, generation_time, data_size)
    
    # Extract continuation usage stats if available
    continuation_stats = None
    if config and config.get("use_eos_continuation_search"):
        # Count how many samples used continuation (if paths provided)
        if paths:
            continuation_count = sum(1 for path in paths if any(
                step.get("continuation_attempt") for step in path
            ))
            continuation_stats = {
                "enabled": True,
                "samples_extended": continuation_count,
                "total_samples": len(paths),
                "percentage": round(100 * continuation_count / len(paths), 1) if paths else 0
            }
        else:
            continuation_stats = {"enabled": True, "samples_extended": "unknown"}

    # Console output
    print(f"\n== Generation Summary ==")
    if config and config.get("name"):
        print(f"Run: {config['name']}")
    
    # Print key config
    print(f"Config: k={k}, seed='{seed}', max_length={max_length}")
    if config:
        important = ["generator_type", "use_eos", "temperature", "use_eos_continuation_search", 
                     "max_continuation_attempts", "enable_trim_v1", "enable_trim_v2"]
        shown = {k: config[k] for k in important if k in config}
        if shown:
            print(f"  {shown}")
    
    print(f"Samples: {metrics.unique_count}/{metrics.total_count} unique")
    print(f"Avg length: {metrics.avg_length:.1f}")
    
    if metrics.generation_time_ms:
        print(f"Time: {metrics.generation_time_ms:.1f}ms")
    
    if metrics.similarity:
        sim = metrics.similarity
        print(f"Similarity to seed:")
        if sim.get("levenshtein_mean"):
            print(f"  Levenshtein: {sim['levenshtein_mean']:.3f}")
        if sim.get("ngram_f1_mean"):
            print(f"  n-gram F1: {sim['ngram_f1_mean']:.3f}")
    if metrics.consonant_vowel_ratio is not None:
        print(f"Consonant/Vowel ratio: {metrics.consonant_vowel_ratio:.3f}")
    
    # Show examples with continuation info
    if continuation_flags:
        # Count how many of the first 3 examples were extended
        num_examples = min(3, len(samples))
        extended_indices = [i for i in range(num_examples) 
                           if i < len(continuation_flags) and continuation_flags[i]]
        extended_count = len(extended_indices)
        print(f"Examples ({extended_count}/{num_examples} extended): {samples[:3]}")
        if extended_indices:
            print(f"Extended index {extended_indices}")
    else:
        print(f"Examples: {samples[:3]}")
    
    # Build complete payload
    payload = {
        "timestamp": _now_iso(),
        "config": config or {},
        "k": k,
        "seed": seed,
        "max_length": max_length,
        "n_requested": n_requested,
        "samples": samples,
        "analysis": asdict(metrics),
        "continuation_stats": continuation_stats,
        "paths": paths
    }
    
    path = _save_json(payload, prefix=log_prefix)
    print(f"[Log saved: {path}]")
    return path