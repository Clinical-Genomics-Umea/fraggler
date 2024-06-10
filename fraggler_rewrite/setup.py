import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setuptools.setup(
    name="fraggler2",
    version="0.1.0",
    description="Rewrite of fraggler",
    url="https://github.com/willros/fraggler",
    author="William Rosenbaum",
    author_email="william.rosenbaum88@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "lmfit",
        "scipy",
        "biopython",
        "panel",
        "altair",
        "setuptools",
        "pandas-flavor",
    ],
    entry_points={"console_scripts": ["fraggler2=fraggler2.fraggler:cli"]},
)