# tests/generator/test_generator_2_performance.py
# Performance tests with actual repository name data. Focus: Algorithm works performantly actual envisioned project data patterns and outputs.
import time
import gc
import tracemalloc
import random
import pytest
from src.trie.trie import Trie
from src.generator.generator import Generator


def _load_words(path, n):
    words = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            w = line.strip()
            if w:
                words.append(w)
    return words

def _build_trie(words, k=2):
    t = Trie(k=k)
    for w in words:
        if len(w) >= t.get_k():
            t.add_word(w)
    return t

def test_generator_performance_duration_under_set_limit(repo_root):
    """
    TEST
    What: Generation latency under a fixed budget
    Why : Ensure generates names quickly
    How : Time generating N names after building a trie from training data
    """
    N_TRAIN = 2000
    N_GEN = 5             # placeholder, tune later
    MAX_LEN = 15
    TIME_LIMIT_S = 5.25   # placeholder, tune later

    words = _load_words(repo_root / "data" / "training_data.txt", N_TRAIN)
    t = _build_trie(words, k=2)
    gen = Generator(t)

    seeds = ["re", "py", "js", "web", "api", "cli", "dev", "data", "ux", "ai"]
    random.seed(1337)

    start = time.time()
    out = []
    for i in range(N_GEN):
        seed = seeds[i % len(seeds)]
        out.append(gen.generate(seed, MAX_LEN))
    duration = time.time() - start

    assert len(out) == N_GEN
    assert all(isinstance(x, str) for x in out)
    assert all(len(x) <= MAX_LEN for x in out if x)
    assert duration < TIME_LIMIT_S, f"Generation too slow: {duration:.3f}s for {N_GEN} names"

@pytest.mark.perf
def test_generator_peak_memory_under_budget(repo_root):
    """
    TEST
    What: Peak memory while generating many names
    Why : Ensure generation is memory-efficient and non-leaky
    How : Measure tracemalloc peak during bulk generation
    """
    N_TRAIN = 2000
    N_GEN = 5        # placeholder, tune later
    MAX_LEN = 15
    LIMIT_MB = 100.0  # placeholder, tune later

    words = _load_words(repo_root / "data" / "training_data.txt", N_TRAIN)
    t = _build_trie(words, k=2)
    gen = Generator(t)

    seeds = ["re", "py", "js", "web", "api", "cli", "dev", "data", "ux", "ai"]
    random.seed(4242)

    gc.collect()
    tracemalloc.start()
    results = []
    for i in range(N_GEN):
        seed = seeds[i % len(seeds)]
        results.append(gen.generate(seed, MAX_LEN))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / (1024 * 1024)
    # Sanity checks
    assert len(results) == N_GEN
    assert all(isinstance(x, str) for x in results)
    assert all(len(x) <= MAX_LEN for x in results if x)

    assert peak_mb < LIMIT_MB, f"Peak {peak_mb:.2f} MiB > {LIMIT_MB} MiB"