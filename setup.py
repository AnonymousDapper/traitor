# type: ignore

from pathlib import Path

from setuptools import setup

requires = Path("requirements.txt").read_text().splitlines()

readme = Path("README.md").read_text()


setup(
    name="traitor",
    author="AnonymousDapper",
    url="https://gitlab.a-sketchy.site/AnonymousDapper/traitor",
    project_urls={},
    version="0.1.0",
    packages=["traitor", "traitor.traits"],
    package_data={},
    license="MIT",
    description="",
    install_requires=requires,
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires=">=3.8.0",
    classifiers=[],
)
