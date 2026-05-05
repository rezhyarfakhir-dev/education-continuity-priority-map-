"""Run the full cleaning pipeline in order; log to logs/run_<timestamp>.txt."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
LOGS = ROOT / "logs"

ORDER = [
    "05_clean_boundaries.py",
    "01_clean_conflict.py",
    "02_clean_displacement.py",
    "03_clean_schools.py",
    "04_clean_access.py",
    "06_compute_scores.py",
    "07_export_leaflet_data.py",
]


def main():
    LOGS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOGS / f"run_{stamp}.txt"

    with open(log_path, "w", encoding="utf-8") as log:
        for name in ORDER:
            header = f"\n{'='*70}\n{name}\n{'='*70}\n"
            print(header, end="")
            log.write(header)
            r = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / name)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
            )
            print(r.stdout, end="")
            log.write(r.stdout)
            if r.returncode != 0:
                print(r.stderr)
                log.write(r.stderr)
                log.write(f"\n!! {name} failed with code {r.returncode}\n")
                sys.exit(r.returncode)
        log.write("\nALL OK\n")
    print(f"\nlog: {log_path}")


if __name__ == "__main__":
    main()
