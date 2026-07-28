from pathlib import Path
from setuptools import find_packages, setup

README = Path(__file__).parent / "README.md"

setup(
    name="face-depth-world-model",
    version="0.1.0",
    description="Monocular face depth estimation and persistent vision world modeling",
    long_description=README.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "numpy",
        "opencv-python",
        "pyyaml",
        "matplotlib",
        "scipy",
    ],
    extras_require={"dev": ["pytest", "black", "isort", "flake8", "mypy"]},
    python_requires=">=3.9",
)
