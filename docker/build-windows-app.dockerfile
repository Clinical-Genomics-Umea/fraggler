FROM tobix/pywine:3.10 as base 

RUN apt-get update && apt-get install -y zip
RUN mkdir -p /build
WORKDIR /build
RUN wine python -m pip install pyinstaller==6.6.0 pyinstaller-versionfile PyYAML

# docker run -v ${PWD}:/build -it win-image
# RUN wine python -m pip install dist/fraggler-3.0.3-py3-none-any.whl 
    # wine create-version-file metadata.yml --outfile file_version_info.txt --version 3.0.3 \
    # wine python -m PyInstaller --name "Fraggler" --noconfirm --onefile --windowed --icon "fraggler/icons/icon.ico" --version-file="file_version_info.txt" --hidden-import "fraggler" --add-data "fraggler/icons;./fraggler/icons/." "fraggler_app.py"