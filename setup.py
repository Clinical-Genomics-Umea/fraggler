import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setuptools.setup(
    name="fraggler",
    version="3.0.1",
    description="Fragment Analysis package in python!",
    url="https://github.com/willros/fraggler",
    author="William Rosenbaum and Pär Larsson",
    author_email="william.rosenbaum@umu.se",
    license="MIT",
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    install_requires=[
        "pandas==2.2.2",
        "numpy==1.26.4",
        "scikit-learn==1.5.0",
        "matplotlib==3.9.0",
        "lmfit==1.3.1",
        "scipy==1.13.1",
        "biopython==1.83",
        "panel==1.4.4",
        "altair==5.3.0",
        "setuptools",
        "pandas-flavor==0.6.0",
    ],
    entry_points={"console_scripts": ["fraggler=fraggler.fraggler:cli"]},
)
