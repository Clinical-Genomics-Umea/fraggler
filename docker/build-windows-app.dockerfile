# Use the pywine image with Python 3.10, which includes Python and Wine setup
FROM tobix/pywine:3.10 as base

# Update package lists and install the zip utility
RUN apt-get update && apt-get install -y zip

# Set up a build directory and set it as the working directory
RUN mkdir -p /build
WORKDIR /build

# Install necessary Python packages using Wine's pip for Windows compatibility
RUN wine python -m pip install pyinstaller==6.6.0 pyinstaller-versionfile PyYAML

# Instructions for using this Docker container to package Fraggler GUI as Windows Executable
#
# Example Usage:
# - Mount the current directory as `/build` inside the container
# - Run interactively to package the application
#
# docker run -v ${PWD}:/build -it win-image
#
# Steps inside the container:
# 1. Install the built wheel file with Wine's Python to prepare for packaging:
#    wine python -m pip install dist/fraggler-3.0.3-py3-none-any.whl 
#
# 2. Create version info for the executable using metadata and version parameters:
#    wine create-version-file metadata.yml --outfile file_version_info.txt --version 3.0.3
#
# 3. Use PyInstaller to package the Python application into a Windows executable with specified options:
#    wine python -m PyInstaller --name "Fraggler" --noconfirm --onefile --windowed --icon "fraggler/icons/icon.ico" \
#    --version-file="file_version_info.txt" --hidden-import "fraggler" \
#    --add-data "fraggler/icons;./fraggler/icons/." "fraggler_app.py"
#
# Notes:
# - `pyinstaller==6.6.0` ensures compatibility with this specific version.
# - `pyinstaller-versionfile` handles version metadata integration for the executable.
# - Adjust paths and file names as needed based on the project structure.
