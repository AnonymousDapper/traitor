# type: ignore

import re
from pathlib import Path

from setuptools import setup

requires = Path("requirements.txt").read_text().splitlines()

readme = Path("README.md").read_text()


setup(
    name="traitor",
    author="AnonymousDapper",
    url="",
    project_urls={},
    version="0.0.1",
    packages=["traitor", "traitor.traits"],
    package_data={},
    license="MIT",
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.8.0",
    classifiers=[],
)
