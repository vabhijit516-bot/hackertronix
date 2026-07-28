import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "results" / "readiness_report.json"


def main():
    pytest_result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, capture_output=True, text=True)
    demo_result = subprocess.run([sys.executable, "scripts/run_demo.py"], cwd=ROOT, capture_output=True, text=True)
    score = 90 if pytest_result.returncode == 0 and demo_result.returncode == 0 else 70
    payload = {
        "score": score,
        "pytest_exit_code": pytest_result.returncode,
        "demo_exit_code": demo_result.returncode,
        "pytest_output": pytest_result.stdout.strip().splitlines()[-5:],
        "demo_output": demo_result.stdout.strip().splitlines()[-5:],
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
