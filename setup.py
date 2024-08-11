import os

from setuptools import find_packages, setup

import versioneer


# Function to parse requirements.txt
def parse_requirements(filename):
    with open(filename, "r") as f:
        return f.read().splitlines()


setup(
    name="steam_sales",  # Name of your package
    version=versioneer.get_version(),  # Initial release version
    cmdclass=versioneer.get_cmdclass(),  # Command line version
    author="DataForgeOpenAIHub",
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
    license="MIT",  # License
    description="CLI for Steam Store Data Ingestion ETL Pipeline",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DataForgeOpenAIHub/Steam-Sales-Analysis",  # Project URL
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Specify minimum Python version if needed
)
