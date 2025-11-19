# Use miniconda as base image
FROM continuumio/miniconda3:latest

# Create a non-root user
ARG USERNAME=devuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y --no-install-recommends sudo \
    && echo $USERNAME ALL=(ALL) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to the non-root user
USER $USERNAME

# Set working directory
WORKDIR /home/$USERNAME/workspace

# Copy environment yml and test requirements
COPY environment.yml test-environment.txt /tmp/conda-tmp/

# Create conda environment from environment.yml
RUN conda env update -n base -f /tmp/conda-tmp/environment.yml && \
    conda clean --all --yes

# Install test dependencies
RUN pip install --user -r /tmp/conda-tmp/test-environment.txt

# Clean up temporary files
RUN rm -rf /tmp/conda-tmp

# Set environment variables
ENV PATH="/opt/conda/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    QT_MAC_WANTS_LAYER=1

# Copy project files
COPY . /home/$USERNAME/workspace

# Install the package in development mode
# NOTE: This is commented out to speed up the build process during development and there are rapid changes to the source code
# TODO: Uncomment here and remove from postCreateCommand in devcontainer.json once development slows down
# RUN pip install --user -e .

# Update PATH for user-installed packages
ENV PATH="/home/$USERNAME/.local/bin:$PATH"

# Set default command
CMD ["/bin/bash"]
