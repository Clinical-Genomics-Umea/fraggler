import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setuptools.setup(
    name="fraggler",
    version="2.0.1",
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
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "networkx",
        "lmfit",
        "scipy",
        "biopython",
        "panel==1.3.8",
        "bokeh==3.3.4",
        "fire",
        "openpyxl",
        "colorama",
        "altair",
        "setuptools",
    ],
    entry_points={"console_scripts": ["fraggler=fraggler.cli:run"]},
)
