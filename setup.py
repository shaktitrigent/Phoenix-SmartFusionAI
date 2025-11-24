"""Setup script for Phoenix-SmartFusionAI."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="phoenix-smartfusionai",
    version="1.0.0",
    description="SmartFusionAI - Unified Engine for BDD + Locators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="shaktitrigent",
    author_email="",
    url="https://github.com/shaktitrigent/Phoenix-SmartFusionAI",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
        "pytest>=7.0.0",
        "pytest-bdd>=7.0.0",
    ],
    extras_require={
        "playwright": ["playwright>=1.40.0"],
        "selenium": ["selenium>=4.15.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smartfusion=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
    ],
)

