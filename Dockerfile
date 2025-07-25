FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install git
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    git \
    curl \
    wget \
    graphviz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up the working directory
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# install quarto for docs rendering
RUN wget -q $(curl https://latest.fast.ai/pre/quarto-dev/quarto-cli/linux-amd64.deb) && \
    dpkg -i quarto*.deb && \
    rm quarto*.deb

WORKDIR /app

# Install the projects dependencies using the req files to optimize layer caching
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --all-extras --active

# Copy the current directory into the container
COPY . .
# Install dependencies using uv
RUN uv sync --active

# Set the default command to an interactive shell
CMD ["/bin/bash"] 