# Use a stable Ubuntu base image
FROM ubuntu:20.04

# Set environment variable to suppress interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install essential tools
RUN apt-get update && \
    apt-get install -y zip curl software-properties-common

# Install Python 3.10 from the deadsnakes PPA repository
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev && \
    # Download and install pip specifically for Python 3.10
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 && \
    # Create symlinks for Python and pip commands for convenience
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    ln -s /usr/local/bin/pip3.10 /usr/bin/pip

# Install the Python package build utility
RUN pip install build

# Set up a dedicated build directory
RUN mkdir -p /build
WORKDIR /build

# Usage:
# - Mount the current directory to `/build` inside the container
# - Run interactively to build Fraggler Python package
#
# Example:
# docker run -v ${PWD}:/build -it pip-image
# python -m build
