# scripts/create_batch_logs.py
# Simple batch runner - reads test configs from JSON and runs them.
# Usage: poetry run python scripts/create_batch_logs.py

import json
import os
import subprocess

CONFIG_PATH = "scripts/create_batch_logs_3.json"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    tests = json.load(f)

for test in tests:
    print(f"\nRunning: {test['name']}")

    cmd = ["python", "-m", "src.main", "--debug-generator"]
    if test.get("temperature", 1.0) != 1.0:
        cmd += ["--temperature", str(test["temperature"])]
    if test.get("enable_trim"):
        cmd.append("--enable-trim")
    if test.get("use_context_shifting"):
        cmd.append("--use-context-shifting")
    if "eos_threshold" in test:
        cmd += ["--eos-threshold", str(test["eos_threshold"])]
    if "max_shifts" in test:
        cmd += ["--max-shifts", str(test["max_shifts"])]

    # EXPERIMENTAL mode = same rule as src/main.py
    is_experimental = (test.get("temperature", 1.0) != 1.0) or bool(test.get("use_context_shifting", False))

    # Build interactive inputs in the exact UI order
    seed = test["seed"]
    max_length = str(test.get("max_length", 10))
    k = str(test.get("k", 2))
    n_suggestions = str(test.get("n_suggestions", 5))
    prefix = ""  # optional

    # data_size: send "" (all) or an integer as string
    ds = test.get("data_size", "")
    data_size = str(ds) if isinstance(ds, int) else ""

    # Only send the EOS answer in BASE mode. In experimental mode the prompt is skipped.
    inputs = [
        seed,
        max_length,
        k,
        n_suggestions,
        prefix,
    ]
    if not is_experimental:
        use_eos_answer = "y" if test.get("use_eos") else "n"
        inputs.append(use_eos_answer)
    inputs += [
        data_size,
        "quit",
    ]

    # Optional env to label runs in your logs
    env = os.environ.copy()
    env["RUN_NAME"] = test.get("name", "")
    if "temperature" in test:
        env["RUN_TEMPERATURE"] = str(test["temperature"])
    env["RUN_ENABLE_TRIM"] = "1" if test.get("enable_trim") else "0"

    subprocess.run(cmd, input="\n".join(inputs), text=True, env=env)

print("\n✅ Done! Check logs/ for results")
