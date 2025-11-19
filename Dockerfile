# Use miniconda as base image
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /workspace

# Copy environment file
COPY environment.yml /tmp/environment.yml

# Create conda environment from environment.yml
RUN conda env update -n base -f /tmp/environment.yml && \
    conda clean --all --yes

# Set environment variables
ENV PATH="/opt/conda/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    QT_MAC_WANTS_LAYER=1

# Copy project files
COPY . /workspace

# Install the package in development mode
RUN pip install -e .

# Install test dependencies
RUN pip install -r test-environment.txt

# Set default command
CMD ["/bin/bash"]
