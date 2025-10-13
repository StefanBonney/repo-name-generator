# scripts/create_batch_logs.py
# Simple batch runner - reads test configs from JSON and runs them.
# Usage: poetry run python scripts/create_batch_logs.py

import json
import os
import subprocess
import re

CONFIG_PATH = "scripts/2025-10-12/create_batch_logs_2.jsonc"

# Read and strip JSONC comments
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    content = f.read()
    # Remove single-line comments (// ...)
    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    # Remove multi-line comments (/* ... */)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove trailing commas before } or ]
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    tests = json.loads(content)

for test in tests:
    print(f"\nRunning: {test['name']}")

    cmd = ["python", "-m", "src.main", "--debug-generator"]
    if test.get("temperature", 1.0) != 1.0:
        cmd += ["--temperature", str(test["temperature"])]
    if test.get("enable_trim_v1"):
        cmd.append("--enable-trim-v1")
    if test.get("enable_trim_v2"):
        cmd.append("--enable-trim-v2")
    if test.get("use_eos_continuation_search"):
        cmd.append("--use-eos-continuation-search")
    if "max_continuation_attempts" in test:
        cmd += ["--max-continuation-attempts", str(test["max_continuation_attempts"])]

    # EXPERIMENTAL mode = same rule as src/main.py
    is_experimental = (
        test.get("temperature", 1.0) != 1.0 
        or test.get("use_eos_continuation_search", False)
        or test.get("enable_trim_v1", False)
        or test.get("enable_trim_v2", False)
    )

    # Build interactive inputs in the exact UI order
    seed = test["seed"]
    max_length = str(test.get("max_length", 10))
    k = str(test.get("k", 2))
    n_suggestions = str(test.get("n_suggestions", 5))
    prefix = ""  # optional

    # data_size: send "" (all) or an integer as string
    # Treat 0 as "all data" (empty string)
    ds = test.get("data_size", "")
    if isinstance(ds, int) and ds > 0:
        data_size = str(ds)
    else:
        data_size = ""

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
        "quit",  # Extra quit to ensure clean exit if UI loops again
        
    ]

    # Optional env to label runs in logs
    env = os.environ.copy()
    env["RUN_NAME"] = test.get("name", "")
    if "temperature" in test:
        env["RUN_TEMPERATURE"] = str(test["temperature"])
    env["RUN_ENABLE_TRIM_V1"] = "1" if test.get("enable_trim_v1") else "0"
    env["RUN_ENABLE_TRIM_V2"] = "1" if test.get("enable_trim_v2") else "0"
    env["RUN_USE_EOS_CONTINUATION"] = "1" if test.get("use_eos_continuation_search") else "0"

    subprocess.run(cmd, input="\n".join(inputs), text=True, env=env)

print("\n✅ Done! Check logs/ for results")