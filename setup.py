from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent
requirements_file = Path(here, "requirements.txt")
if requirements_file.is_file():
    with open(requirements_file, "r") as fs:
        requirements = fs.read().splitlines()
else:
    requirements = []
setup(
    name="pyinit",
    version="1.0",
    description="A python project initializer",
    author="temme",
    packages=find_packages(),
    install_requires=requirements,
)
