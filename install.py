import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def install_requirements():
    requirements = [
        "numpy",
        "opencv-python",
        "PyYAML",
        "matplotlib",
        "scipy",
        "pytest",
        "fastapi",
        "uvicorn",
    ]
    subprocess.check_call([sys.executable, "-m", "pip", "install", *requirements])


if __name__ == "__main__":
    install_requirements()
    print("Dependencies installed successfully.")
