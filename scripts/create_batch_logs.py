# Simple batch runner - reads test configs from JSON and runs them.
# poetry run python scripts/create_batch_logs.py

import subprocess
import json

# Load test configurations
with open("scripts/create_batch_logs.json", "r") as f:
    tests = json.load(f)

# Run each test
for test in tests:
    print(f"\nRunning: {test['name']}")
    
    # Build command
    cmd = ["python", "-m", "src.main", "--debug-generator"]
    if test.get("temperature", 1.0) != 1.0:
        cmd.extend(["--temperature", str(test["temperature"])])
    if test.get("enable_trim"):
        cmd.append("--enable-trim")
    
    # Build inputs
    inputs = [
        test["seed"],
        str(test.get("max_length", 10)),
        str(test.get("k", 2)),
        str(test.get("n_suggestions", 5)),
        "",  # prefix
        "y" if test.get("use_eos") else "n",
        str(test.get("data_size", ""))
    ]
    inputs.append("quit")
    
    # Run
    subprocess.run(cmd, input="\n".join(inputs), text=True)

print("\n✅ Done! Check logs/ for results")