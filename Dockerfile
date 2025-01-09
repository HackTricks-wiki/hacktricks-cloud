# Dockerfile
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
      curl \
      wget \
      git \
      sudo \
      python3.12 \
      python3-pip \
      build-essential \
      && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip3 install --upgrade pip

# Install Python dependencies
RUN pip3 install openai tqdm tiktoken

# Install Rust & Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install mdBook & plugins
RUN cargo install mdbook
RUN cargo install mdbook-alerts
RUN cargo install mdbook-reading-time
RUN cargo install mdbook-pagetoc
RUN cargo install mdbook-tabs
RUN cargo install mdbook-codename

WORKDIR /app
