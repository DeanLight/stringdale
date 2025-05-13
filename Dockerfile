FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install git
RUN apt-get update && \
    apt-get install -y \
    git \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the current directory into the container
COPY . .
# Install dependencies using uv
RUN uv pip install '.[dev]'


# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser
# Give ownership of /app directory to appuser
RUN chown -R appuser:appuser /app
# Switch to non-root user
USER appuser

# Set the default command to an interactive shell
CMD ["/bin/bash"] 