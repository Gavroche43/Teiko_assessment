# Use Ubuntu as base
FROM ubuntu:latest

# Install system dependencies
RUN apt update && apt install -y python3 python3-pip python3-venv

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and install Python packages
RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install pandas matplotlib numpy scipy

# Set the default Python path to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Default command
CMD ["python3"]
