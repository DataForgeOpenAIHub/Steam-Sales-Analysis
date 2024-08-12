import os

from setuptools import find_packages, setup

import versioneer


# Function to parse requirements.txt
def parse_requirements(filename):
    with open(filename, "r") as f:
        return f.read().splitlines()


setup(
    name="steamstore_etl",  # Name of your package
    version=versioneer.get_version(),  # Initial release version
    cmdclass=versioneer.get_cmdclass(),  # Command line version
    packages=find_packages(),  # Automatically find and include all packages
    include_package_data=True,  # Include data files specified in MANIFEST.in
    install_requires=parse_requirements(
        os.path.join(os.path.dirname(__file__), "requirements.txt")
    ),  # Use requirements.txt
    entry_points={
        "console_scripts": [
            "steamstore=steam_sales.app:app",
        ],
    },
    python_requires=">=3.10",  # Specify minimum Python version if needed
)
