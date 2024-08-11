from setuptools import setup, find_packages


# Function to parse requirements.txt
def parse_requirements(filename):
    with open(filename, "r") as f:
        return f.read().splitlines()


setup(
    name="steam_sales",  # Name of your package
    version="0.1.0",  # Initial release version
    packages=find_packages(),  # Automatically find and include all packages
    include_package_data=True,  # Include data files specified in MANIFEST.in
    install_requires=parse_requirements("requirements.txt"),  # Use requirements.txt
    entry_points={
        "console_scripts": [
            "steamstore=steam_sales.app:app",
        ],
    },
    description="CLI for Steam Store Data Ingestion ETL Pipeline",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/steam_sales",  # Project URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Specify minimum Python version if needed
)
